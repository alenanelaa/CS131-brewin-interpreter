from interpreterv1 import Interpreter
import sys
import os
import io

class BrewinTestCase:
    def __init__(self, input_file, expected_output_file):
        self.input_file = input_file
        self.expected_output_file = expected_output_file

    def run_test(self, interpreter):
        with open(self.input_file, 'r') as f:
            input_lines = f.read().splitlines()

        expected_output = ""
        with open(self.expected_output_file, 'r') as f:
            expected_output = f.read()

        output = io.StringIO()
        sys.stdout = output

        interpreter.run(input_lines)
        actual_output = output.getvalue()

        sys.stdout = sys.__stdout__

        if actual_output.strip() != expected_output.strip():
            print(f"Test case failed: {self.input_file}")
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
        input_file = os.path.join(test_dir, filename)
        expected_output_file = os.path.join(expected_dir, filename.replace(".brewin", ".out"))
        test_cases.append(BrewinTestCase(input_file, expected_output_file))

interpreter = Interpreter()
num_tests = len(test_cases)
num_passed = 0

for test_case in test_cases:
    if test_case.run_test(interpreter):
        num_passed += 1

print(f"{num_passed}/{num_tests} test cases passed")

# actual_output = io.StringIO()
# sys.stdout = actual_output

# def read_file(filename):
#     with open(filename, 'r') as f:
#         lines = f.read().splitlines()
#     return lines

# if __name__ == '__main__':
#     if len(sys.argv) != 2:
#         print(f"Usage: python3 {sys.argv[0]} filename")
#         sys.exit(1)
#     filename = sys.argv[1]
    
#     lines = read_file(filename)
#     interpreter = Interpreter()

#     interpreter.run(lines)

#     output = actual_output.getvalue()
#     sys.stdout = sys.__stdout__

#     print(output, end='')