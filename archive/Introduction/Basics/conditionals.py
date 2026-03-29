
# === Conditionals Syntax ===
# Demonstration of various conditional styles in Python

def separator(title):
    print(f"\n=== {title} ===")

# 1. if/elif/else chain with multiple conditions
separator("1. if/elif/else chain with multiple conditions")
val = 7
if val < 0:
    print(f"{val} is negative")
elif val == 0:
    print("Zero")
elif 0 < val < 5:
    print(f"{val} is small positive")
else:
    print(f"{val} is large positive")

# 2. Nested if
separator("2. Nested if")
val = 2
if val % 2 == 0:
    print(f"{val} is even")
    if val % 4 == 0:
        print(f"{val} is divisible by 4")
    else:
        print(f"{val} is not divisible by 4")

# 3. Single-line if
separator("3. Single-line if")
if val > 0: print(f"{val} is positive (inline)")

# 4. Ternary operator
separator("4. Ternary conditional expression")
status = "OK" if val % 2 == 0 else "FAIL"
print(f"Status: {status}")

# 5. Conditional assignment with or
separator("5. Conditional assignment using or")
user_input = ""
default = "default_value"
# if user_input is falsy, assign default
result = user_input or default
print(f"Result: {result}")

# 6. Conditional execution using and
separator("6. Conditional execution using and")
def action():
    print("Action executed")

trigger = True
trigger and action()

# 7. for-else as conditional
separator("7. for-else for search")
target = 3
for i in [1, 2, 4, 5]:
    if i == target:
        print("Found target")
        break
else:
    print("Target not found in list")

# 8. Error handling via condition
separator("8. Simulated error check")
value = -1
if value < 0:
    print("Error: negative value")
    # raise ValueError("Negative")
else:
    print("Value is non-negative")
