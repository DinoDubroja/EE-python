# 1. Literal definitions
a = 10               # decimal literal
b = 0b1010           # binary literal (10 in decimal)
c = 0o12             # octal literal (10 in decimal)
d = 0xA              # hexadecimal literal (10 in decimal)

print(a, b, c, d)    # → 10 10 10 10


# 2. Basic arithmetic
x = 7
y = 3
print(x + y)         # addition        → 10
print(x - y)         # subtraction     → 4
print(x * y)         # multiplication  → 21
print(x // y)        # integer division→ 2
print(x % y)         # modulo          → 1
print(x ** y)        # exponentiation  → 343


# 3. In-place operators
x = 5
x += 2               # x = x + 2
print(x)             # → 7
x *= 3               # x = x * 3
print(x)             # → 21


# 4. Comparison & Boolean context
n = 0
if n:
    print("Nonzero")
else:
    print("Zero")    # → Zero

print(5 > 3, 5 == 3, 5 < 3)  # → True False False


# 5. Bitwise operations
flags = 0b0011
MASK  = 0b0101
print(flags & MASK)  # AND → 0b0001 (1)
print(flags | MASK)  # OR  → 0b0111 (7)
print(flags ^ MASK)  # XOR → 0b0110 (6)
print(~flags)        # NOT → bitwise complement

n = -5            # …11111011 in two’s-complement
print(n & 0xFF)   # 251  (masking gives last 8 bits)
print(n >> 1)     # -3   (arithmetic shift)


# 6. Converting to/from strings
num = 255
s_dec = str(num)                       # "255"
s_hex = format(num, 'x')               # "ff"
s_bin = format(num, '08b')             # "11111111"
print(s_dec, s_hex, s_bin)

# parse back from string
print(int("ff", 16), int("1010", 2))    # → 255 10


# 7. Useful built-ins
import math
print(math.factorial(5))   # 120
print(math.gcd(24, 36))    # 12
print(math.isqrt(17))      # integer sqrt → 4


# 8. Random integers
import random
rand_int = random.randint(1, 100)      # inclusive 1–100
print(rand_int)


# 9. Practical example: sampling indices
length = 20
step = 3
indices = list(range(0, length, step))
print(indices)        # [0, 3, 6, 9, 12, 15, 18]


# 10. Overflow & big ints
big = 2**100
print(big)           # Python handles arbitrarily large ints


# 11. int() from float: truncation, not rounding
print(int(3.9))   # 3
print(int(-3.9))  # -3


# 12. Invalid literal → ValueError
for s in ["123", "0b101", "0b102", "xyz"]:
    try:
        print(s, "→", int(s, base=0))
    except ValueError as e:
        print("Bad literal:", s)


# 13. Underscores in numeric literals (Python ≥3.6)
million = 1_000_000
print("One million:", million)



