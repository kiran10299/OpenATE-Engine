import sys
import time
from open_ate.core.sequence import StepResult, TestStatus

class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

class CliRunner:
    """Renders real-time ATE sequence progress tree to terminal."""

    @staticmethod
    def print_banner(sequence_name: str, uut_serial: str):
        print(f"\n{Color.CYAN}{'='*75}{Color.RESET}")
        print(f"{Color.BOLD}OpenATE Test Executive | Senior Test Engineering Framework{Color.RESET}")
        print(f"Sequence : {Color.BOLD}{sequence_name}{Color.RESET}")
        print(f"UUT S/N  : {Color.BOLD}{uut_serial}{Color.RESET}")
        print(f"{Color.CYAN}{'='*75}{Color.RESET}\n")
        print(f"{'STATUS':<8} | {'STEP NAME':<38} | {'MEASURED':<12} | {'LIMITS'}")
        print("-" * 75)

    @staticmethod
    def on_step_completed(res: StepResult):
        if res.status == TestStatus.PASSED:
            tag = f"{Color.GREEN}[PASS]{Color.RESET}"
        elif res.status == TestStatus.FAILED:
            tag = f"{Color.RED}[FAIL]{Color.RESET}"
        elif res.status == TestStatus.ERROR:
            tag = f"{Color.YELLOW}[ERR ]{Color.RESET}"
        else:
            tag = f"{Color.CYAN}[SKIP]{Color.RESET}"

        meas_str = f"{res.measured_value:.4f} {res.limit.unit if res.limit else ''}" if res.measured_value is not None else "--"
        limit_str = str(res.limit) if res.limit else "None"

        print(f"{tag:<17} | {res.step_name:<38} | {meas_str:<12} | {limit_str}")

    @staticmethod
    def print_summary(report_data: dict):
        print("-" * 75)
        verdict = report_data["verdict"]
        col = Color.GREEN if verdict == "PASSED" else Color.RED
        print(f"\nFINAL VERDICT : {Color.BOLD}{col}{verdict}{Color.RESET}")
        print(f"Total Steps   : {report_data['total_steps']} (Passed: {report_data['passed_steps']}, Failed: {report_data['failed_steps']}, Errors: {report_data['error_steps']})")
        print(f"Execution Time: {report_data['duration_sec']:.3f} seconds\n")
