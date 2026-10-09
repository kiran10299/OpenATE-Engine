from typing import Dict, Any, Type
from open_ate.hal.base import BaseInstrument, BasePowerSupply, BaseDMM, BaseOscilloscope
from open_ate.hal.sim_psu import SimulatedPowerSupply
from open_ate.hal.sim_dmm import SimulatedDMM
from open_ate.hal.sim_scope import SimulatedOscilloscope

class InstrumentFactory:
    """Factory creating appropriate instrument drivers (Physical SCPI/VISA or Virtual Simulation)."""

    _REGISTRY: Dict[str, Type[BaseInstrument]] = {
        "SIM_PSU": SimulatedPowerSupply,
        "SIM_DMM": SimulatedDMM,
        "SIM_SCOPE": SimulatedOscilloscope,
    }

    @classmethod
    def create(cls, driver_type: str, resource_name: str, name: str) -> BaseInstrument:
        key = driver_type.upper()
        if key not in cls._REGISTRY:
            raise ValueError(f"Unknown instrument driver '{driver_type}'. Available: {list(cls._REGISTRY.keys())}")
        return cls._REGISTRY[key](resource_name=resource_name, name=name)

    @classmethod
    def register_driver(cls, driver_name: str, driver_class: Type[BaseInstrument]) -> None:
        cls._REGISTRY[driver_name.upper()] = driver_class
