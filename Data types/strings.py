# 1. Literal definitions
s1 = "Hello, world!"
s2 = 'Python is fun'
s3 = """This
is a
multi-line
string."""
print(s1, s2, s3, sep="\n---\n")


# 2. Concatenation & repetition
a = "EE"
b = "ngineering"
print(a + b)         # 'EEngineering'
print("ha" * 3)      # 'hahaha'


# 3. Indexing & slicing
msg = "Measurement"
print(msg[0])        # 'M'
print(msg[-1])       # 't'
print(msg[3:7])      # 'sure'
print(msg[:4], msg[4:], sep=" | ")  # 'Meas' | 'urement'


# 4. Immutability
try:
    msg[0] = "m"
except TypeError as e:
    print("Strings are immutable:", e)
# Characters in a string cannot be changed directly onece created


# 5. Common methods
text = "  PyVISA & NumPy  "
print(text.lower())         # '  pyvisa & numpy  '
print(text.strip())         # 'PyVISA & NumPy'
print(text.replace("NumPy", "SciPy"))  # '  PyVISA & SciPy  '
print(text.split("&"))      # ['  PyVISA ', ' NumPy  ']
print("-".join(["A","B","C"]))  # 'A-B-C'


# 6. f-strings & formatting
name = "Oscilloscope"
value = 3.3
unit = "V"
print(f"{name}: {value:.2f} {unit}")  # 'Oscilloscope: 3.30 V'


# 7. Raw strings & escapes
path = r"C:\Users\EE\Projects"
print(path)  # backslashes are literal
print("Line1\nLine2")  # newline escape
print(r"Line1\nLine2")  # raw string, no escape


# 8. Searching & slicing
log = "Error: Voltage out of range at 12:34:56"
if "Error" in log:
    timestamp = log.split()[-1]  # Extracting the last word as timestamp
    print("Timestamp:", timestamp)


# 9. Formatting templates (for dynamic reports)
from string import Template
t = Template("Channel $ch: $val $unit")
print(t.substitute(ch=1, val=1.23, unit="mA"))

# 10. Strings length
long = "A" * 10_000_000
print(len(long))

