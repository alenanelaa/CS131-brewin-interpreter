from interpreterv1 import Interpreter
import sys
import os
import io

class BrewinTestCase:
    def __init__(self, src_file, expected_output_file, inp=None):
        self.src_file = src_file
        self.expected_output_file = expected_output_file
        self.stdin = inp
        self.interpreter = Interpreter(inp=self.stdin)

    def run_test(self):
        with open(self.src_file, 'r') as f:
            src_lines = f.read().splitlines()

        expected_output = ""
        with open(self.expected_output_file, 'r') as f:
            expected_output = f.read()

        output = io.StringIO()
        sys.stdout = output

        self.interpreter.run(src_lines)
        actual_output = output.getvalue()

        sys.stdout = sys.__stdout__

        if actual_output.strip() != expected_output.strip():
            print(f"Test case failed: {self.src_file}")
            print("Expected output:")
            print(expected_output)
            print("Actual output:")
            print(actual_output, end = '')
            return False

        return True


test_dir = "test-cases"
expected_dir = "expected-output"

test_cases = []
for filename in os.listdir(test_dir):
    if filename.endswith(".brewin"):
        source_file = os.path.join(test_dir, filename)
        expected_output_file = os.path.join(expected_dir, filename.replace(".brewin", ".out"))
        try:
            inputfile = os.path.join(test_dir, filename.replace(".brewin", ".in"))
            with open(inputfile, encoding="utf-8") as f:
                stdin = list(map(lambda x: x.rstrip("\n"), f.readlines()))
        except FileNotFoundError:
            stdin = None
        test_cases.append(BrewinTestCase(source_file, expected_output_file, inp = stdin))

num_tests = len(test_cases)
num_passed = 0

for test_case in test_cases:
    if test_case.run_test():
        num_passed += 1

print(f"{num_passed}/{num_tests} test cases passed")