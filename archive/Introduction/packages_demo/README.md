
# Python Packages & Modules Demo

This project demonstrates how to organize and use modules and packages in Python.

## Structure

```
Packages demo/
├── package1/
│   ├── __init__.py
│   └── yapper.py         # Example: random string generator
├── package2/
│   ├── __init__.py
│   └── math.py           # Example: integer average function
└── main.py               # Example usage script
```

## How to Use


## Importing Modules: Examples

You can import and use modules in several ways:

### 1. Import a function directly
```python
from package1.yapper import yap
from package2.math import average

print(yap(8))            # Prints a random 8-letter string
print(average([1,2,3]))  # Prints 2
```

### 2. Import the whole module
```python
import package1.yapper
import package2.math

print(package1.yapper.yap(5))
print(package2.math.average([4,5,6]))
```

### 3. Import with alias
```python
import package1.yapper as yp
import package2.math as m

print(yp.yap(6))
print(m.average([10, 20, 30]))
```

### 4. Import all from module (not recommended for large modules)
```python
from package1.yapper import *
from package2.math import *

print(yap(7))
print(average([7,8,9]))
```

## Running main.py
You can create a `main.py` to demonstrate importing and using your packages as shown above.

## Notes
- Each package directory contains an `__init__.py` file (can be empty) to mark it as a Python package.
- You can add more modules to each package as needed.
- This structure is suitable for both small and larger Python projects.

