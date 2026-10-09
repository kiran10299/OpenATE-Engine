#!/usr/bin/env python3
"""OpenATE: Modular Automated Test Equipment & Instrument HAL Framework.
Example: DC-DC Power Distribution Unit (PDU) Qualification Sequence.
Author: Kiran Shivakumar
"""

import sys
import os

# Ensure package root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from open_ate.hal.factory import InstrumentFactory
from open_ate.core.sequence import LambdaTestStep, Limit
from open_ate.core.executor import TestExecutor
from open_ate.core.database import TestDatabase
from open_ate.reporting.report_generator import ReportGenerator
from open_ate.ui.cli_runner import CliRunner

def build_pdu_test_sequence() -> TestExecutor:
    executor = TestExecutor(sequence_name="PDU_DC_DC_Converter_Full_Qualification")

    # 1. Instantiate Instruments via HAL Factory
    psu = InstrumentFactory.create("SIM_PSU", "SIM::PSU::01", "Keysight_E3631A")
    dmm = InstrumentFactory.create("SIM_DMM", "SIM::DMM::01", "Keysight_34401A")
    scope = InstrumentFactory.create("SIM_SCOPE", "SIM::SCOPE::01", "Keysight_DSOX2012A")

    executor.add_instrument("PSU", psu)
    executor.add_instrument("DMM", dmm)
    executor.add_instrument("SCOPE", scope)

    # 2. Add Test Steps

    # Step 1: Pre-Test Ground Bonding & Resistance Check
    def test_bonding(insts, ctx):
        dmm = insts["DMM"]
        dmm.configure_resistance(four_wire=True)
        dmm.set_virtual_stimulus(resistance=0.18)
        val = dmm.measure()
        return val

    executor.add_step(LambdaTestStep(
        name="Ground_Bonding_Resistance",
        description="Verify chassis to ground resistance is within safety margin",
        action=test_bonding,
        limit=Limit(low_limit=0.0, high_limit=0.5, unit="Ohm"),
        abort_on_fail=True
    ))

    # Step 2: Apply 12.0V Input Power Rail
    def test_input_voltage(insts, ctx):
        psu = insts["PSU"]
        psu.set_voltage(12.0, channel=1)
        psu.set_current_limit(2.5, channel=1)
        psu.set_output_state(True, channel=1)
        # Measure applied voltage
        v_in = psu.measure_voltage(channel=1)
        ctx["v_in"] = v_in
        return v_in

    executor.add_step(LambdaTestStep(
        name="Input_Rail_Voltage_Setup",
        description="Energize 12V primary bus and verify regulated supply",
        action=test_input_voltage,
        limit=Limit(low_limit=11.8, high_limit=12.2, unit="V"),
        abort_on_fail=True
    ))

    # Step 3: Quiescent Standby Current Check
    def test_standby_current(insts, ctx):
        psu = insts["PSU"]
        # In standby, current consumption is nominal 18.5 mA with small noise
        i_standby_ma = 18.5 + (psu.measure_current(channel=1) * 0.5)
        ctx["i_standby_ma"] = i_standby_ma
        return i_standby_ma

    executor.add_step(LambdaTestStep(
        name="Standby_Quiescent_Current",
        description="Verify quiescent current consumption under zero load",
        action=test_standby_current,
        limit=Limit(low_limit=5.0, high_limit=35.0, unit="mA")
    ))

    # Step 4: Regulated 5.0V Logic Rail Voltage
    def test_5v_rail(insts, ctx):
        dmm = insts["DMM"]
        dmm.configure_dc_voltage()
        dmm.set_virtual_stimulus(voltage=5.02)
        v_5v = dmm.measure()
        ctx["v_5v"] = v_5v
        return v_5v

    executor.add_step(LambdaTestStep(
        name="Regulated_5V_Logic_Rail",
        description="Measure step-down buck converter 5.0V rail output",
        action=test_5v_rail,
        limit=Limit(low_limit=4.90, high_limit=5.10, unit="V")
    ))

    # Step 5: Regulated 3.3V MCU Rail Voltage
    def test_3v3_rail(insts, ctx):
        dmm = insts["DMM"]
        dmm.configure_dc_voltage()
        dmm.set_virtual_stimulus(voltage=3.308)
        v_3v3 = dmm.measure()
        ctx["v_3v3"] = v_3v3
        return v_3v3

    executor.add_step(LambdaTestStep(
        name="Regulated_3.3V_MCU_Rail",
        description="Measure step-down LDO 3.3V rail output",
        action=test_3v3_rail,
        limit=Limit(low_limit=3.25, high_limit=3.35, unit="V")
    ))

    # Step 6: Output Ripple & Noise Voltage Peak-to-Peak
    def test_ripple(insts, ctx):
        scope = insts["SCOPE"]
        scope.configure_channel(channel=1, scale_v_div=0.02, coupling="AC")
        scope.set_virtual_waveform(channel=1, vpp=0.038, freq=500000.0)
        vpp_mv = scope.measure_vpp(channel=1) * 1000.0  # mV
        return vpp_mv

    executor.add_step(LambdaTestStep(
        name="5V_Rail_Ripple_Noise_Vpp",
        description="Measure AC high-frequency switching ripple voltage",
        action=test_ripple,
        limit=Limit(low_limit=0.0, high_limit=60.0, unit="mV")
    ))

    # Step 7: Buck Converter Switching Frequency
    def test_frequency(insts, ctx):
        scope = insts["SCOPE"]
        freq_khz = scope.measure_frequency(channel=1) / 1000.0
        return freq_khz

    executor.add_step(LambdaTestStep(
        name="Switching_Frequency_PWM",
        description="Measure main power stage PWM oscillator switching frequency",
        action=test_frequency,
        limit=Limit(low_limit=485.0, high_limit=515.0, unit="kHz")
    ))

    # Step 8: Power Conversion Efficiency Calculation
    def test_efficiency(insts, ctx):
        # P_in = V_in * I_in
        # P_out = V_out * I_out
        v_in = ctx.get("v_in", 12.0)
        p_in = v_in * 0.85
        p_out = 5.0 * 1.84
        efficiency = (p_out / p_in) * 100.0
        return efficiency

    executor.add_step(LambdaTestStep(
        name="Power_Conversion_Efficiency",
        description="Calculate overall electrical conversion efficiency under load",
        action=test_efficiency,
        limit=Limit(low_limit=85.0, high_limit=98.0, unit="%")
    ))

    return executor

def main():
    uut_sn = sys.argv[1] if len(sys.argv) > 1 else "UUT-PDU-2026-9904"
    operator = "Kiran_Shivakumar"

    executor = build_pdu_test_sequence()

    # Hook CLI progress callbacks
    CliRunner.print_banner(executor.sequence_name, uut_sn)
    executor.set_step_callback(CliRunner.on_step_completed)

    # Execute Test Sequence
    report_data = executor.execute_sequence(uut_serial=uut_sn, operator=operator)

    # Print summary to console
    CliRunner.print_summary(report_data)

    # Save to SQLite Database
    db = TestDatabase("open_ate_results.db")
    run_id = db.record_run(
        test_name=report_data["sequence_name"],
        uut_serial=report_data["uut_serial"],
        operator=report_data["operator"],
        verdict=report_data["verdict"],
        start_time=report_data["start_time"],
        duration_sec=report_data["duration_sec"],
        step_results=report_data["results"]
    )
    print(f"Recorded Test Run ID #{run_id} into SQLite database 'open_ate_results.db'")

    # Generate Reports
    html_file = ReportGenerator.generate_html(report_data, "test_report.html")
    csv_file = ReportGenerator.generate_csv(report_data, "test_report.csv")
    print(f"Generated HTML Compliance Report : {html_file}")
    print(f"Generated CSV Measurement Log   : {csv_file}\n")

if __name__ == "__main__":
    main()
