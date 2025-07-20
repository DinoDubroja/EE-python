
# === Tuple Syntax Reference ===

# 1. Tuple creation
empty_tuple = ()
single_element = (42,)  # Note the comma!
numbers = (1, 2, 3, 4, 5)
mixed = (1, "two", 3.0, True)
print("empty_tuple:", empty_tuple)
print("single_element:", single_element)
print("numbers:", numbers)
print("mixed:", mixed)

# 2. Indexing & slicing
first = numbers[0]         # 1
last = numbers[-1]         # 5
middle = numbers[1:4]      # (2, 3, 4)
print("first element:", first)
print("last element:", last)
print("middle slice [1:4]:", middle)

# 3. Tuple unpacking
a, b, c, d, e = numbers
print("unpacked:", a, b, c, d, e)

# 4. Nested tuples
nested = ((1, 2), (3, 4), (5, 6))
print("nested tuple:", nested)
print("first nested tuple:", nested[0])
print("second element of second tuple:", nested[1][1])

# 5. Tuple methods
count_2 = numbers.count(2)     # Count occurrences of 2
index_3 = numbers.index(3)     # Index of first occurrence of 3
print("count of 2:", count_2)
print("index of 3:", index_3)

# 6. Immutability demonstration
# numbers[0] = 10  # Uncommenting this line will raise TypeError

# 7. Membership and length
print("Is 3 in numbers?", 3 in numbers)
print("Length of numbers:", len(numbers))

# 8. Concatenation and repetition
more = (6, 7)
combined = numbers + more
repeated = numbers * 2
print("combined tuple:", combined)
print("repeated tuple:", repeated)

# 9. Tuple comprehension (not possible, but generator expression is)
gen = (x**2 for x in numbers)  # This is a generator, not a tuple
print("generator from tuple:", list(gen))

# 10. Conversion between list and tuple
as_list = list(numbers)
as_tuple = tuple(as_list)
print("as list:", as_list)
print("as tuple:", as_tuple)
