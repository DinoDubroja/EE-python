# loops_syntax.py
# Comprehensive coverage of Python loop constructs with print statements and edge cases

def separator(title):
    print(f"\n=== {title} ===")

# 1. Basic for loop over a list
data = [10, 20, 30]
separator("for loop over list")
for x in data:
    print(x)

# 2. For loop with tuple unpacking
pairs = [(1, 2), (3, 4), (5, 6)]
separator("for loop with tuple unpacking")
for a, b in pairs:
    print(f"a={a}, b={b}")

# 3. For loop using range
separator("for loop with range")
for i in range(5):  # 0 to 4
    print(i)

separator("for loop with range(start, stop, step)")
for i in range(1, 10, 3):
    print(i)

# 4. While loop
separator("while loop")
c = 0
while c < 3:
    print(c)
    c += 1

# 5. While-else construct
separator("while-else (no break)")
n = 0
while n < 2:
    print(n)
    n += 1
else:
    print("Finished without break")

# 6. For-else construct
separator("for-else (break vs no break)")
for v in [1, 2, 3]:
    if v == 4:
        print("Found 4")
        break
    print(v)
else:
    print("Loop ended without finding 4")

# 7. Break and continue
data = [0, 1, 2, 3, 4]
separator("break and continue")
for num in data:
    if num % 2 == 0:
        print(f"Skipping even: {num}")
        continue
    if num > 3:
        print(f"Breaking on: {num}")
        break
    print(f"Processing odd: {num}")

# 8. Nested loops
matrix = [[1, 2], [3, 4]]
separator("nested loops")
for row in matrix:
    for val in row:
        print(val)

# 9. Modifying list during iteration (edge case)
lst = [1, 2, 3]
separator("modify list during iteration")
for x in lst:
    print(f"x={x}, lst={lst}")
    if x == 2:
        lst.append(4)
print("Final lst:", lst)

# 10. Iterator exhaustion and StopIteration
separator("iterator exhaustion")
it = iter([1, 2])
print(next(it))
print(next(it))
try:
    print(next(it))
except StopIteration:
    print("StopIteration caught")

# 11. Infinite loop with break
separator("infinite loop with break")
i = 0
while True:
    print(i)
    i += 1
    if i >= 2:
        print("Breaking infinite loop")
        break
