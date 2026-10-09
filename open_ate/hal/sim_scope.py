import random
import time
from open_ate.hal.base import BaseOscilloscope

class SimulatedOscilloscope(BaseOscilloscope):
    """Simulated 2-Channel 200MHz Digital Oscilloscope mimicking Keysight DSO-X 2012A."""

    def __init__(self, resource_name: str = "SIM::SCOPE::01", name: str = "Simulated_Keysight_DSOX2012A"):
        super().__init__(resource_name, name)
        self.simulated = True
        self.channels = {
            1: {"scale": 1.0, "coupling": "DC", "input_vpp": 3.3, "input_freq": 1000.0},
            2: {"scale": 1.0, "coupling": "DC", "input_vpp": 5.0, "input_freq": 50.0},
        }

    def connect(self) -> bool:
        time.sleep(0.05)
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.is_connected = False
        return True

    def reset(self) -> None:
        self.is_connected = True

    def get_id(self) -> str:
        return "KEYSIGHT TECHNOLOGIES,DSO-X 2012A,SIM9940129,02.41.2018042400"

    def configure_channel(self, channel: int, scale_v_div: float, coupling: str = "DC") -> None:
        if channel in self.channels:
            self.channels[channel]["scale"] = scale_v_div
            self.channels[channel]["coupling"] = coupling

    def configure_timebase(self, time_s_div: float) -> None:
        pass

    def set_virtual_waveform(self, channel: int, vpp: float, freq: float) -> None:
        if channel in self.channels:
            self.channels[channel]["input_vpp"] = float(vpp)
            self.channels[channel]["input_freq"] = float(freq)

    def measure_vpp(self, channel: int = 1) -> float:
        ch = self.channels.get(channel, self.channels[1])
        noise = random.gauss(0, 0.015 * ch["input_vpp"])
        return max(0.0, ch["input_vpp"] + noise)

    def measure_frequency(self, channel: int = 1) -> float:
        ch = self.channels.get(channel, self.channels[1])
        noise = random.gauss(0, 0.0005 * ch["input_freq"])
        return max(0.0, ch["input_freq"] + noise)

    def measure_vrms(self, channel: int = 1) -> float:
        vpp = self.measure_vpp(channel)
        # Sine wave Vrms = Vpp / (2 * sqrt(2))
        return vpp / (2.0 * math.sqrt(2)) if 'math' in globals() else vpp / 2.8284

import math
