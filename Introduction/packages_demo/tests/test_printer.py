
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import package1.printer as printer

def test_print_uppercase(capsys):
    printer.printUpperCase("hello world")
    captured = capsys.readouterr()
    # .title() capitalizes each word
    assert captured.out.strip() == "HELLO WORLD"