# sets.py
# Demonstration of Python set operations with printed results

# Creating sets
empty = set()
fruits = {"apple", "banana", "cherry"}
from_list = set([1, 2, 2, 3, 3, 3])  # duplicates removed
print("empty set:", empty)
print("fruits set:", fruits)
print("from list (duplicates removed):", from_list)

# Membership tests
print("Is 'banana' in fruits?", "banana" in fruits)
print("Is 4 not in from_list?", 4 not in from_list)

# Add, remove, discard
fruits.add("date")
print("After add('date'):", fruits)
fruits.remove("apple")  # KeyError if not present
print("After remove('apple'):", fruits)
fruits.discard("kiwi")   # No error if not present
print("After discard('kiwi'):", fruits)

# Pop & clear
popped = fruits.pop()     # Removes and returns an arbitrary element
print("Popped element:", popped)
print("Remaining fruits:", fruits)
fruits.clear()
print("After clear():", fruits)

# Set algebra
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7}
print("A:", A)
print("B:", B)
print("A union B:", A | B)
print("A intersection B:", A & B)
print("A difference B (A - B):", A - B)
print("Symmetric difference (A ^ B):", A ^ B)

# Comprehensions: filter even numbers
evens = {x for x in range(10) if x % 2 == 0}
print("Even numbers 0-9:", evens)

# EE use case: unique channel IDs from readings
readings = [(1, 0.12), (2, 0.23), (1, 0.13), (3, 0.34)]
channels = {ch for ch, val in readings}
print("Unique channel IDs:", channels)

# Edge case: '{}' creates empty dict, not set
empty_braces = {}
print("Type of {}:", type(empty_braces))
