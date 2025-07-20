def separator(title):
    print(f"\n=== {title} ===")
a = True
b = False
y = 0b1100  # 12
def true_func():
    print("true_func called")
    return True
def false_func():
    print("false_func called")
    return False

# === Logical Operators Syntax ===
# Demonstration of various logical and bitwise operations in Python

def separator(title):
    print(f"\n=== {title} ===")

# 1. Boolean operators: and, or, not
separator("1. Boolean operators: and, or, not")
a = True
b = False
print(f"a and b: {a and b}")
print(f"a or b: {a or b}")
print(f"not a: {not a}")

# 2. XOR via bitwise ^
separator("2. Bitwise XOR on bools")
print(f"a ^ b: {a ^ b}")  # True if exactly one True
print(f"b ^ b: {b ^ b}")

# 3. XOR via != on bools
separator("3. XOR via !=")
print(f"a != b: {a != b}")
print(f"a != a: {a != a}")

# 4. XOR via 'is not'
separator("4. XOR via 'is not'")
# For booleans, 'is not' gives same as !=
print(f"a is not b: {a is not b}")
print(f"a is not a: {a is not a}")

# 5. Bitwise on integers for logic
separator("5. Bitwise operations on ints")
x = 0b1010  # 10
y = 0b1100  # 12
print(f"x & y: {bin(x & y)}")  # AND
print(f"x | y: {bin(x | y)}")  # OR
print(f"x ^ y: {bin(x ^ y)}")  # XOR
print(f"~x: {bin(~x)}")        # NOT (two's complement)

# 6. Short-circuit evaluation demonstration
separator("6. Short-circuit evaluation demonstration")
def true_func():
    print("true_func called")
    return True

def false_func():
    print("false_func called")
    return False

separator("Short-circuit AND")
# false_func() returned False, so true_func() is not called
if False and true_func():
    pass

separator("Short-circuit OR")
# true_func() returned True, so false_func() is not called
if True or false_func():
    pass
