
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

1. **Importing from a package:**
   ```python
   from package1.yapper import yap
   from package2.math import average
   ```

2. **Example usage:**
   ```python
   print(yap(8))            # Prints a random 8-letter string
   print(average([1,2,3])) # Prints 2
   ```

3. **Running main.py:**
   You can create a `main.py` to demonstrate importing and using your packages.

## Notes
- Each package directory contains an `__init__.py` file (can be empty) to mark it as a Python package.
- You can add more modules to each package as needed.
- This structure is suitable for both small and larger Python projects.

