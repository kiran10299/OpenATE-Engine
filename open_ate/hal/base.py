from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time

class BaseInstrument(ABC):
    """Abstract Base Class for all physical and simulated test bench instruments."""

    def __init__(self, resource_name: str, name: str = "GenericInstrument"):
        self.resource_name = resource_name
        self.name = name
        self.is_connected = False
        self.simulated = False

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection with instrument via VISA / SCPI / TCP / Serial."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Safely terminate instrument session and leave outputs in a safe state."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Send *RST command to bring instrument to default factory state."""
        pass

    @abstractmethod
    def get_id(self) -> str:
        """Query standard *IDN? identification string."""
        pass


class BasePowerSupply(BaseInstrument):
    """Hardware Abstraction for Programmable DC Power Supplies (e.g. Keysight E3631A, Chroma)."""

    @abstractmethod
    def set_voltage(self, voltage_volts: float, channel: int = 1) -> None:
        pass

    @abstractmethod
    def set_current_limit(self, current_amps: float, channel: int = 1) -> None:
        pass

    @abstractmethod
    def set_output_state(self, enabled: bool, channel: int = 1) -> None:
        pass

    @abstractmethod
    def measure_voltage(self, channel: int = 1) -> float:
        pass

    @abstractmethod
    def measure_current(self, channel: int = 1) -> float:
        pass


class BaseDMM(BaseInstrument):
    """Hardware Abstraction for Digital Multimeters (e.g. Keysight 34401A, Fluke 8846A)."""

    @abstractmethod
    def configure_dc_voltage(self, range_val: Optional[float] = None) -> None:
        pass

    @abstractmethod
    def configure_resistance(self, four_wire: bool = False) -> None:
        pass

    @abstractmethod
    def configure_current(self, dc: bool = True) -> None:
        pass

    @abstractmethod
    def measure(self) -> float:
        pass


class BaseOscilloscope(BaseInstrument):
    """Hardware Abstraction for Digital Storage Oscilloscopes (e.g. Keysight DSO-X 2012A, Tektronix)."""

    @abstractmethod
    def configure_channel(self, channel: int, scale_v_div: float, coupling: str = "DC") -> None:
        pass

    @abstractmethod
    def configure_timebase(self, time_s_div: float) -> None:
        pass

    @abstractmethod
    def measure_vpp(self, channel: int = 1) -> float:
        pass

    @abstractmethod
    def measure_frequency(self, channel: int = 1) -> float:
        pass

    @abstractmethod
    def measure_vrms(self, channel: int = 1) -> float:
        pass
