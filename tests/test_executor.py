import pytest
from open_ate.core.sequence import LambdaTestStep, Limit, TestStatus
from open_ate.core.executor import TestExecutor, SequenceVerdict

def test_executor_pass_flow():
    executor = TestExecutor("UnitTest_Pass")
    step1 = LambdaTestStep(
        name="Step_5V_Check",
        action=lambda insts, ctx: 5.01,
        limit=Limit(low_limit=4.9, high_limit=5.1, unit="V")
    )
    executor.add_step(step1)
    res = executor.execute_sequence(uut_serial="TEST-001")

    assert res["verdict"] == "PASSED"
    assert res["passed_steps"] == 1
    assert res["failed_steps"] == 0

def test_executor_fail_flow():
    executor = TestExecutor("UnitTest_Fail")
    step1 = LambdaTestStep(
        name="Step_Out_Of_Spec",
        action=lambda insts, ctx: 12.8,
        limit=Limit(low_limit=11.5, high_limit=12.2, unit="V")
    )
    executor.add_step(step1)
    res = executor.execute_sequence(uut_serial="TEST-002")

    assert res["verdict"] == "FAILED"
    assert res["failed_steps"] == 1
