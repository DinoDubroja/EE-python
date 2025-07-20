
# === List Syntax Reference ===
# Demonstration of Python list operations and comprehensions with printed results

# 1. Create lists
empty_list = []
primes = [2, 3, 5, 7, 11]
mixed = [1, "two", 3.0, True]
print("empty_list:", empty_list)
print("primes:", primes)
print("mixed:", mixed)

# 2. Indexing & slicing
first = primes[0]      # 2
last = primes[-1]      # 11
middle = primes[1:4]   # [3, 5, 7]
every_even = primes[::2]  # [2, 5, 11]
print("first element:", first)
print("last element:", last)
print("middle slice [1:4]:", middle)
print("every other element:", every_even)

# 3. Append, extend, insert
primes.append(13)
print("after append(13):", primes)
primes.extend([17, 19])
print("after extend([17,19]):", primes)
primes.insert(0, 1)
print("after insert(0,1):", primes)

# 4. Remove & pop
primes.remove(1)
print("after remove(1):", primes)
last_prime = primes.pop()
print("popped last element:", last_prime)
second = primes.pop(1)
print("popped element at index 1:", second)
primes.clear()
print("after clear():", primes)

# 5. Count & index
data = [0,1,2,1,0,1,2,1]
c1 = data.count(1)
i2 = data.index(2)
print("data:", data)
print("count of 1s:", c1)
print("first index of 2:", i2)

# 6. Sort, reverse, copy
vals = [3, 1, 4, 1, 5]
sorted_vals = sorted(vals)
print("original vals:", vals)
print("sorted_vals = sorted(vals):", sorted_vals)
vals.sort()
print("after vals.sort():", vals)
vals.reverse()
print("after vals.reverse():", vals)
vals_copy = vals.copy()
print("copy of vals:", vals_copy)

# 7. Nesting lists (e.g., matrix or multiple channels)
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]
element = matrix[1][2]
print("matrix:", matrix)
print("element at [1][2]:", element)

# 8. List comprehensions
squares = [x**2 for x in range(10)]
evnsq   = [x for x in range(20) if x % 2 == 0]
pairs   = [(x, y) for x in [1,2] for y in [3,4]]
adc_readings = [0.12, 0.55, 0.03, 0.78, 0.34]
scaled        = [r * 3.3 for r in adc_readings]
clean         = [v for v in scaled if v > 0.1]
print("squares 0-9:", squares)
print("evens 0-19:", evnsq)
print("pairs:", pairs)
print("adc_readings:", adc_readings)
print("scaled readings:", scaled)
print("clean (filtered) readings:", clean)

# 9. Moving average using sliding window
window_size = 3
mov_avg = [
    sum(adc_readings[i:i+window_size]) / window_size
    for i in range(len(adc_readings) - window_size + 1)
]
print("moving average (window=3):", mov_avg)

# 10. List duplication and extension
myList = [1, 2, 3]  # Example of a list variable
myList = myList*2  # Duplicate the list
print("myList after duplication:", myList)
myList = myList + [4, 5]  # Extend the list with more elements
print("myList after duplication and extension:", myList)
