# 1. Literal definitions
a = 3.14           # decimal float
b = 1.0e3          # scientific notation → 1000.0
c = -2.5e-4        # small number → -0.00025
print(a, b, c)


# 2. Comparisons & Boolean context
print(0.0 == False)     # True, since False == 0.0
print(bool(0.0))        # False

# Watch out for precision:
print(0.1 + 0.2 == 0.3) # False


# 3. Rounding & formatting
val = 2.34567
print(round(val, 2))                             # → 2.35
print(f"{val:.3f}")                              # → '2.346'
print(format(val, '10.4f'))                      # → '    2.3457'


# 4. Converting to/from strings
s = "123.456"
f = float(s)
print(f, type(f))
print(str(0.0001234), repr(0.0001234))


# 5. Useful math functions
import math
print(math.floor(3.7))      # 3
print(math.ceil(3.1))       # 4
print(math.trunc(-4.9))     # -4
frac, whole = math.modf(5.75)
print("frac:", frac, "whole:", whole)


# 6. Special float values
pos_inf = float('inf')
neg_inf = float('-inf')
nan     = float('nan')
print(pos_inf > 1e308, neg_inf < -1e308, nan != nan)


# 7. Decimal module for high-precision
from decimal import Decimal, getcontext
getcontext().prec = 10
d1 = Decimal('0.1')
d2 = Decimal('0.2')
print(d1 + d2 == Decimal('0.3'))   # True


# 8. Formatting very large/small
print(f"{1.23e10:.2e}")            # '1.23e+10'
print(f"{1.23e-10:.3e}")           # '1.23e-10'