import pytest
from open_ate.hal.sim_psu import SimulatedPowerSupply
from open_ate.hal.sim_dmm import SimulatedDMM
from open_ate.hal.sim_scope import SimulatedOscilloscope
from open_ate.hal.factory import InstrumentFactory

def test_sim_psu_lifecycle():
    psu = SimulatedPowerSupply()
    assert not psu.is_connected
    assert psu.connect() is True
    assert psu.is_connected is True

    psu.set_voltage(5.0, channel=1)
    psu.set_output_state(True, channel=1)
    v = psu.measure_voltage(channel=1)
    assert 4.90 < v < 5.10

    psu.disconnect()
    assert not psu.is_connected

def test_sim_dmm_measurements():
    dmm = SimulatedDMM()
    dmm.connect()
    dmm.configure_dc_voltage()
    dmm.set_virtual_stimulus(voltage=3.30)
    val = dmm.measure()
    assert 3.28 < val < 3.32

def test_instrument_factory():
    psu = InstrumentFactory.create("SIM_PSU", "SIM::1", "TestPSU")
    assert isinstance(psu, SimulatedPowerSupply)
    scope = InstrumentFactory.create("SIM_SCOPE", "SIM::2", "TestScope")
    assert isinstance(scope, SimulatedOscilloscope)
