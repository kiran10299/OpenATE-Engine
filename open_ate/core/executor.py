from enum import Enum
import time
import datetime
from typing import List, Dict, Any, Optional, Callable
from open_ate.core.sequence import TestStep, StepResult, TestStatus, Limit
from open_ate.hal.base import BaseInstrument

class SequenceVerdict(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    ABORTED = "ABORTED"

class TestExecutor:
    """Multi-threaded ATE Sequence Execution Engine with Instrument Lifecycle Management."""
    __test__ = False

    def __init__(self, sequence_name: str = "Standard_ATE_Sequence"):
        self.sequence_name = sequence_name
        self.steps: List[TestStep] = []
        self.instruments: Dict[str, BaseInstrument] = {}
        self.context: Dict[str, Any] = {}
        self.step_callback: Optional[Callable[[StepResult], None]] = None
        self.is_aborted = False

    def add_instrument(self, key: str, instrument: BaseInstrument) -> None:
        self.instruments[key] = instrument

    def add_step(self, step: TestStep) -> None:
        self.steps.append(step)

    def set_step_callback(self, callback: Callable[[StepResult], None]) -> None:
        self.step_callback = callback

    def abort(self) -> None:
        self.is_aborted = True

    def execute_sequence(self, uut_serial: str, operator: str = "Test_Engineer") -> Dict[str, Any]:
        """Runs the entire test suite, tracks results, and gracefully cleans up instruments."""
        self.is_aborted = False
        start_time = datetime.datetime.now()
        t0 = time.time()
        results: List[StepResult] = []
        overall_passed = True

        # Phase 1: Connect all instruments
        for name, inst in self.instruments.items():
            if not inst.is_connected:
                inst.connect()

        # Phase 2: Execute Steps sequentially
        try:
            for step in self.steps:
                if self.is_aborted:
                    res = StepResult(step.name)
                    res.status = TestStatus.SKIPPED
                    results.append(res)
                    continue

                res = StepResult(step.name)
                res.limit = step.limit
                step_t0 = time.time()

                try:
                    val = step.execute(self.instruments, self.context)
                    res.measured_value = val
                    res.duration_seconds = time.time() - step_t0

                    # Evaluate against engineering limits
                    if step.limit:
                        passed = step.limit.evaluate(val)
                        res.status = TestStatus.PASSED if passed else TestStatus.FAILED
                    else:
                        res.status = TestStatus.PASSED

                except Exception as e:
                    res.status = TestStatus.ERROR
                    res.error_message = str(e)
                    res.duration_seconds = time.time() - step_t0

                results.append(res)

                if self.step_callback:
                    self.step_callback(res)

                if res.status != TestStatus.PASSED:
                    overall_passed = False
                    if step.abort_on_fail:
                        self.is_aborted = True

        finally:
            # Phase 3: Teardown / Safe State
            for name, inst in self.instruments.items():
                try:
                    inst.reset()
                except Exception:
                    pass

        duration_sec = time.time() - t0
        verdict = SequenceVerdict.PASSED if overall_passed else SequenceVerdict.FAILED
        if self.is_aborted:
            verdict = SequenceVerdict.ABORTED

        return {
            "sequence_name": self.sequence_name,
            "uut_serial": uut_serial,
            "operator": operator,
            "verdict": verdict.value,
            "start_time": start_time,
            "duration_sec": duration_sec,
            "results": results,
            "total_steps": len(self.steps),
            "passed_steps": sum(1 for r in results if r.status == TestStatus.PASSED),
            "failed_steps": sum(1 for r in results if r.status == TestStatus.FAILED),
            "error_steps": sum(1 for r in results if r.status == TestStatus.ERROR),
        }
