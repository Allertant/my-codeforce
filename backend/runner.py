import subprocess
import time
import os
import sys
from typing import List, Dict, Tuple

class CodeRunner:
    def __init__(self, timeout: float = 2.0, max_output: int = 1024 * 1024):
        self.timeout = timeout
        self.max_output = max_output

    def run_all(self, code: str, samples: List[Dict], work_dir: str) -> List[Dict]:
        """Run all test cases and return results."""
        results = []
        
        # Write temporary code file for execution
        temp_code_path = os.path.join(work_dir, "_temp_runner.py")
        with open(temp_code_path, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            for i, case in enumerate(samples):
                result = self._run_single(temp_code_path, case["input"], case["expected_output"], work_dir)
                result["id"] = i + 1
                results.append(result)
        finally:
            if os.path.exists(temp_code_path):
                os.remove(temp_code_path)
        
        return results

    def _run_single(self, code_path: str, stdin: str, expected: str, work_dir: str) -> Dict:
        start_time = time.time()
        
        # Environment detection: prefer .venv if exists in project root
        # (Assuming project root is two levels up from work_dir: e.g. root/800/prob.py)
        # However, for simplicity here, we'll try to find .venv in the current root
        python_exe = sys.executable
        # Try to find .venv in the parent of the work_dir (the project root)
        project_root = os.path.dirname(work_dir)
        venv_python = os.path.join(project_root, ".venv", "bin", "python")
        if os.path.exists(venv_python):
            python_exe = venv_python

        try:
            process = subprocess.Popen(
                [python_exe, code_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=work_dir
            )
            
            stdout, stderr = process.communicate(input=stdin, timeout=self.timeout)
            duration = (time.time() - start_time) * 1000 # ms
            
            # Clean outputs for comparison
            passed = self._compare(stdout, expected)
            
            return {
                "status": "AC" if passed else "WA",
                "stdout": stdout[:self.max_output],
                "stderr": stderr[:self.max_output],
                "duration": round(duration, 2),
                "exitCode": process.returncode
            }

        except subprocess.TimeoutExpired:
            # Handle TLE
            # On Unix, kill the process group might be safer but for local simple scripts process.kill() is okay
            process.kill()
            return {
                "status": "TLE",
                "stdout": "",
                "stderr": "Time Limit Exceeded",
                "duration": self.timeout * 1000,
                "exitCode": -1
            }
        except Exception as e:
            return {
                "status": "RE",
                "stdout": "",
                "stderr": str(e),
                "duration": 0,
                "exitCode": 1
            }

    def _compare(self, actual: str, expected: str) -> bool:
        """Minimalistic comparison: ignore trailing spaces and empty lines."""
        def clean(s: str):
            return "\n".join([line.rstrip() for line in s.strip().splitlines() if line.strip()])
        
        return clean(actual) == clean(expected)
