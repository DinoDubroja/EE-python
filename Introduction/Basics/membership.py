
# === Membership & Identity Checks ===
# Demonstration of membership and identity checks in Python

def separator(title):
    print(f"\n=== {title} ===")

# 1. Membership in sequences
separator("1. Membership in sequences")
seq = [1, 2, 3]
print("2 in seq?", 2 in seq)
print("5 not in seq?", 5 not in seq)

s = {'a', 'b', 'c'}
print("'b' in set?", 'b' in s)

# 2. Dictionary key membership
separator("2. Dictionary key membership")
d = {'x': 100}
print("'x' in dict?", 'x' in d)

# 3. Identity: is / is not
separator("3. Identity: is / is not")
a = None
b = None
print("a is None?", a is None)
print("a is b?", a is b)
x = [1]
y = [1]
print("x == y?", x == y)
print("x is y?", x is y)

# 4. Equal operator on custom objects
separator("4. Equal operator on custom objects")
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __eq__(self, other):
        return isinstance(other, Vector) and self.x == other.x and self.y == other.y
v1 = Vector(1,2)
v2 = Vector(1,2)
print("v1 == v2?", v1 == v2)
print("v1 is v2?", v1 is v2)

# 5. Safe dict access vs exception
separator("5. Safe dict access vs exception")
d = {'k':42}
print("d.get('k'):", d.get('k'))
print("d.get('z', 'missing'):", d.get('z', 'missing'))
try:
    print(d['z'])
except KeyError as e:
    print("KeyError caught for missing key 'z':", e)

# 6. any() / all() for membership logic
separator("6. any() / all() for membership logic")
nums = [0, 2, 4, 5]
print("any odd?", any(n % 2 for n in nums))
print("all even?", all(n % 2 == 0 for n in nums))

# 7. Regex membership via re.search
separator("7. Regex membership via re.search")
import re
s = "Error: code 404"
print("Has error code?", bool(re.search(r"Error", s)))
print("Has digit sequence?", bool(re.search(r"\d+", s)))
