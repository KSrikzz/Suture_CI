import subprocess
import os

class Validator:
    def __init__(self):
        pass

    def check_syntax(self, file_path):
        """Verifies if the Python file has any syntax errors."""
        print(f"[*] Validating syntax for: {file_path}")
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", file_path],
                capture_output=True,
                text=True,
                check=True
            )
            print("[+] Validation Passed: Syntax is correct.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Validation Failed: Syntax error detected.")
            print(f"DEBUG: {e.stderr}")
            return False

    def run_unit_tests(self, test_command="pytest"):
        """Optional: Runs the project's test suite."""
        try:
            subprocess.run(test_command.split(), check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
        
    def check_syntax_with_feedback(self, file_path):
        try:
            subprocess.run(["python", "-m", "py_compile", file_path], capture_output=True, text=True, check=True)
            return True, None
        except subprocess.CalledProcessError as e:
            return False, e.stderr