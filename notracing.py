from interpreterv2 import Interpreter
import sys

class BrewinTestCase:
    def __init__(self, src_file):
        self.src_file = src_file
        self.interpreter = Interpreter()

    def run_test(self):
        with open(self.src_file, 'r') as f:
            src_lines = f.read().splitlines()

        self.interpreter.run(src_lines)

if len(sys.argv) < 2:
    print("Usage: python3 custom-test.py <brewin test case>")
    sys.exit(1)

filename = sys.argv[1]
test = BrewinTestCase(filename)

test.run_test()