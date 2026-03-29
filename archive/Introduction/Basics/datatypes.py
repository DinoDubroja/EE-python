a = 3

# === Python Data Types Syntax ===

# 1. Numbers
a = 10     # Integer
b = 2.5    # Floating point number
c = 1+2j   # Complex number
print(type(a), type(b), type(c))  # Output: <class 'int'> <class 'float'> <class 'complex'>

# 2. Boolean values
is_true = True
is_false = False
print(is_true, is_false)  # Output: True False

a = 3
b = 2
print(a > b)   # Output: True
print(a == b)  # Output: False

# 3. Strings
s1 = 'Hello'  # Single-quoted string
s2 = "World"  # Double-quoted string
combined = s1 + ' ' + s2  # String concatenation
print(combined)  # Output: Hello World

name = "Alice"
age = 30
print(f"{name} is {age} years old.")  # Output: Alice is 30 years old.
