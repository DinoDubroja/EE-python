
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import package1.yapper as yapper
import string

def test_yap_length_and_chars():
    s = yapper.yap(8)
    assert isinstance(s, str)
    assert len(s) == 8
    assert all(c in string.ascii_letters for c in s)

def test_yap_zero():
    assert yapper.yap(0) == ""
