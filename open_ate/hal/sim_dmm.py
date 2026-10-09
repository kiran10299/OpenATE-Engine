import random
import time
from typing import Optional
from open_ate.hal.base import BaseDMM

class SimulatedDMM(BaseDMM):
    """Simulated 6.5-Digit Precision Digital Multimeter mimicking Keysight 34401A."""

    def __init__(self, resource_name: str = "SIM::DMM::01", name: str = "Simulated_Keysight_34401A"):
        super().__init__(resource_name, name)
        self.simulated = True
        self.mode = "VOLT:DC"
        self.range_val = 10.0
        self.virtual_source_voltage = 5.0
        self.virtual_source_resistance = 1000.0

    def connect(self) -> bool:
        time.sleep(0.03)
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.is_connected = False
        return True

    def reset(self) -> None:
        self.mode = "VOLT:DC"
        self.range_val = 10.0

    def get_id(self) -> str:
        return "HEWLETT-PACKARD,34401A,SIM8821901,A.02.14-02.40-00.08"

    def configure_dc_voltage(self, range_val: Optional[float] = None) -> None:
        self.mode = "VOLT:DC"
        if range_val:
            self.range_val = range_val

    def configure_resistance(self, four_wire: bool = False) -> None:
        self.mode = "FRES" if four_wire else "RES"

    def configure_current(self, dc: bool = True) -> None:
        self.mode = "CURR:DC" if dc else "CURR:AC"

    def set_virtual_stimulus(self, voltage: float = 5.0, resistance: float = 1000.0) -> None:
        """Inject virtual electrical stimulus from upstream circuit under test."""
        self.virtual_source_voltage = float(voltage)
        self.virtual_source_resistance = float(resistance)

    def measure(self) -> float:
        if not self.is_connected:
            raise ConnectionError(f"Instrument {self.name} is not connected.")

        time.sleep(0.02)  # Emulate integration time (NPLC)

        if self.mode == "VOLT:DC":
            noise = random.gauss(0, 0.00015 * self.virtual_source_voltage)
            return self.virtual_source_voltage + noise
        elif self.mode in ("RES", "FRES"):
            noise = random.gauss(0, 0.001 * self.virtual_source_resistance)
            return self.virtual_source_resistance + noise
        elif self.mode == "CURR:DC":
            # I = V / R
            val = (self.virtual_source_voltage / max(1.0, self.virtual_source_resistance))
            return val + random.gauss(0, 0.00005)
        return 0.0
