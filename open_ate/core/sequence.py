from enum import Enum
from typing import Dict, Any, Optional, Callable, List
import time

class TestStatus(Enum):
    __test__ = False
    NOT_RUN = "NOT_RUN"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class Limit:
    """Evaluates test measurement against specified engineering tolerance limits."""

    def __init__(
        self,
        low_limit: Optional[float] = None,
        high_limit: Optional[float] = None,
        unit: str = "",
        comparison: str = "GELE"  # Greater-Equal-Less-Equal
    ):
        self.low_limit = low_limit
        self.high_limit = high_limit
        self.unit = unit
        self.comparison = comparison.upper()

    def evaluate(self, measured_val: float) -> bool:
        if self.comparison == "GELE":  # low <= val <= high
            if self.low_limit is not None and measured_val < self.low_limit:
                return False
            if self.high_limit is not None and measured_val > self.high_limit:
                return False
            return True
        elif self.comparison == "GT":
            return measured_val > (self.low_limit or 0)
        elif self.comparison == "LT":
            return measured_val < (self.high_limit or 0)
        elif self.comparison == "EQ":
            return abs(measured_val - (self.low_limit or 0)) < 1e-5
        return True

    def __str__(self):
        parts = []
        if self.low_limit is not None:
            parts.append(f">= {self.low_limit}")
        if self.high_limit is not None:
            parts.append(f"<= {self.high_limit}")
        return f"{' and '.join(parts)} {self.unit}".strip()


class StepResult:
    """Data container holding measurement result, verdict, and execution duration."""

    def __init__(self, step_name: str):
        self.step_name = step_name
        self.status = TestStatus.NOT_RUN
        self.measured_value: Optional[float] = None
        self.limit: Optional[Limit] = None
        self.duration_seconds: float = 0.0
        self.error_message: Optional[str] = None
        self.extra_data: Dict[str, Any] = {}


class TestStep:
    """Atomic test step in an ATE sequence."""

    def __init__(
        self,
        name: str,
        description: str = "",
        limit: Optional[Limit] = None,
        abort_on_fail: bool = False
    ):
        self.name = name
        self.description = description
        self.limit = limit
        self.abort_on_fail = abort_on_fail

    def execute(self, instruments: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Override this method to interact with instruments and return numeric measurement."""
        raise NotImplementedError("Subclasses must implement execute().")


class LambdaTestStep(TestStep):
    """Convenience step wrapping an arbitrary callable or lambda."""

    def __init__(
        self,
        name: str,
        action: Callable[[Dict[str, Any], Dict[str, Any]], float],
        description: str = "",
        limit: Optional[Limit] = None,
        abort_on_fail: bool = False
    ):
        super().__init__(name, description, limit, abort_on_fail)
        self.action = action

    def execute(self, instruments: Dict[str, Any], context: Dict[str, Any]) -> float:
        return self.action(instruments, context)
