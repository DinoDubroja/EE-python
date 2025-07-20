# branching.py
# Comprehensive examples of Python branching (if/elif/else) covering syntax variations and edge cases

def separator(title):
    print(f"\n=== {title} ===")

# 1. Simple if
separator("Simple if")
val = 5
if val > 0:
    print(f"{val} is positive")

# 2. if-else
separator("if-else")
val = -3
if val >= 0:
    print(f"{val} is non-negative")
else:
    print(f"{val} is negative")

# 3. if-elif-else chain
separator("if-elif-else chain")
val = 0
if val < 0:
    print(f"{val} is negative")
elif val == 0:
    print(f"{val} is zero")
elif 0 < val < 10:
    print(f"{val} is between 1 and 9")
else:
    print(f"{val} is 10 or greater")

# 4. Nested if
separator("Nested if")
val = 7
if val > 0:
    print("Positive start")
    if val % 2 == 0:
        print(f"{val} is even")
    else:
        print(f"{val} is odd")

# 5. Single-line if (no else)
separator("Single-line if")
val = 2
if val % 2 == 0: print(f"{val} is even (inline)")

# 6. Ternary conditional expression
separator("Ternary expression")
val = 3
parity = "even" if val % 2 == 0 else "odd"
print(f"{val} is {parity}")

# 7. Truthiness checks
separator("Truthiness")
for item in [0, 1, "", "text", [], [1], None]:
    if item:
        print(f"{item!r} is truthy")
    else:
        print(f"{item!r} is falsey")

# 8. Short-circuiting and/or
separator("Short-circuit and/or")
def side_effect():
    print("side_effect() called")
    return False

# AND: second not called if first is False
print("AND short-circuit:")
if False and side_effect():
    pass
# OR: second not called if first is True
print("OR short-circuit:")
if True or side_effect():
    pass

# 9. Membership tests
separator("Membership tests")
seq = [1,2,3]
print("2 in seq?", 2 in seq)
print("5 not in seq?", 5 not in seq)

# 10. Identity vs equality
separator("Identity vs equality")
a = None
b = None
print("a is None?", a is None)
print("a is b?", a is b)
# equality
x = [1]
y = [1]
print("x == y?", x == y)
print("x is y?", x is y)

# 11. pass statement
separator("pass statement")
val = 10
if val == 10:
    pass  # placeholder, no action
print("After pass")

# 12. Error case: invalid comparison types
separator("Invalid comparison types")
try:
    result = 5 < "10"
except TypeError as e:
    print("TypeError caught:", e)

# 13. Complex chained comparisons
separator("Chained comparisons")
x = 5
print("1 < x < 10?", 1 < x < 10)
print("x < 1 < 10?", x < 1 < 10)

# End of branching examples
