
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import package2.math as m

def test_average_non_empty():
    assert m.average([1, 2, 3, 4]) == 2
    assert m.average([0, 5]) == 2

def test_average_empty():
    assert m.average([]) == 0

def test_increment_default():
    assert m.increment(10) == 11

def test_increment_custom_step():
    assert m.increment(10, step=5) == 15
