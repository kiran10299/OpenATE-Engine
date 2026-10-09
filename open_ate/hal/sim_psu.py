import random
import time
from open_ate.hal.base import BasePowerSupply

class SimulatedPowerSupply(BasePowerSupply):
    """Simulated 3-Channel Programmable DC Power Supply mimicking Keysight E3631A."""

    def __init__(self, resource_name: str = "SIM::PSU::01", name: str = "Simulated_Keysight_E3631A"):
        super().__init__(resource_name, name)
        self.simulated = True
        self.channels = {
            1: {"v_set": 0.0, "i_limit": 1.0, "enabled": False, "load_r": 10.0},
            2: {"v_set": 0.0, "i_limit": 1.0, "enabled": False, "load_r": 25.0},
            3: {"v_set": 0.0, "i_limit": 1.0, "enabled": False, "load_r": 50.0},
        }

    def connect(self) -> bool:
        time.sleep(0.04)  # Emulate I/O latency
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        for ch in self.channels:
            self.channels[ch]["enabled"] = False
        self.is_connected = False
        return True

    def reset(self) -> None:
        self.disconnect()
        self.connect()

    def get_id(self) -> str:
        return "KEYSIGHT TECHNOLOGIES,E3631A,SIM0049281,REV-2.4"

    def set_voltage(self, voltage_volts: float, channel: int = 1) -> None:
        if not self.is_connected:
            raise ConnectionError(f"Instrument {self.name} is not connected.")
        if channel not in self.channels:
            raise ValueError(f"Invalid channel {channel}. Valid: 1..3")
        self.channels[channel]["v_set"] = float(voltage_volts)

    def set_current_limit(self, current_amps: float, channel: int = 1) -> None:
        if not self.is_connected:
            raise ConnectionError(f"Instrument {self.name} is not connected.")
        self.channels[channel]["i_limit"] = float(current_amps)

    def set_output_state(self, enabled: bool, channel: int = 1) -> None:
        if not self.is_connected:
            raise ConnectionError(f"Instrument {self.name} is not connected.")
        self.channels[channel]["enabled"] = bool(enabled)

    def measure_voltage(self, channel: int = 1) -> float:
        ch = self.channels[channel]
        if not ch["enabled"]:
            return 0.0
        # Add tiny voltage ripple (0.05%)
        noise = random.gauss(0, 0.002 * ch["v_set"])
        return max(0.0, ch["v_set"] + noise)

    def measure_current(self, channel: int = 1) -> float:
        ch = self.channels[channel]
        if not ch["enabled"] or ch["v_set"] <= 0.0:
            return 0.0
        # Ohm's law with noise
        ideal_i = ch["v_set"] / ch["load_r"]
        actual_i = min(ideal_i, ch["i_limit"])
        noise = random.gauss(0, 0.001)
        return max(0.0, actual_i + noise)
