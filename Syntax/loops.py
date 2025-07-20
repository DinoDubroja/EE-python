
# === Loops Syntax ===
# Demonstration of various loop constructs in Python covering edge cases

def separator(title):
    print(f"\n=== {title} ===")

# 1. Basic for loop over iterable
separator("1. Basic for loop over iterable")
data = [10, 20, 30]
for x in data:
    print(x)

# 2. For loop with range and step
separator("2. For loop with range and step")
for i in range(0, 10, 2):
    print(i)

# 3. While loop with else
separator("3. While loop with else")
c = 3
while c > 0:
    print(c)
    c -= 1
else:
    print("Loop completed without break")

# 4. Break in loops
separator("4. Break in loops")
for x in range(5):
    if x == 3:
        print("Breaking at 3")
        break
    print(x)
else:
    print("Else after break? Skipped because break")

# 5. Continue in loops
separator("5. Continue in loops")
for x in range(5):
    if x % 2 == 0:
        continue
    print(f"Odd number: {x}")

# 6. Nested loops with labeled break simulation
separator("6. Nested loops with labeled break simulation")
found = False
for i in range(1, 4):
    for j in range(1, 4):
        print(i, j)
        if i * j == 6:
            found = True
            break
    if found:
        print("Product 6 found, exiting outer loop")
        break

# 7. Looping over dictionary
separator("7. Looping over dictionary")
d = {'a': 1, 'b': 2}
for key, val in d.items():
    print(key, val)

# 8. List comprehension vs generator expression
separator("8. List comprehension vs generator expression")
sq_list = [x*x for x in range(5)]
sq_gen  = (x*x for x in range(5))
print("list comp:", sq_list)
print("gen comp first 2:", next(sq_gen), next(sq_gen))

# 9. Infinite loop safety
separator("9. Infinite loop safety")
i = 0
while True:
    print(i)
    i += 1
    if i >= 2:
        print("Breaking infinite loop")
        break

# 10. Loop with mutable iteration
separator("10. Loop with mutable iteration")
l = [1, 2, 3, 4]
for x in l[:]:  # Iterate over a copy to avoid skipping elements
    if x % 2 == 0:
        l.remove(x)
print("List after removing evens during iteration:", l)
