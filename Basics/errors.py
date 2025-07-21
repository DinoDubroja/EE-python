# error_handling.py
# Demonstration of Python error handling and exception syntax with examples and printed results

def separator(title):
    print(f"\n=== {title} ===")

# 1. Basic try/except\    
separator("Basic try/except")
try:
    x = 1 / 0
except ZeroDivisionError as e:
    print(f"Caught error: {e}")

# 2. Catch multiple exception types
separator("Catch multiple exceptions")
try:
    import non_existent_module
except (ImportError, ModuleNotFoundError) as e:
    print(f"Import failure: {e}")

# 3. Generic exception (avoid in production)
separator("Generic except")
try:
    {}['key']
except Exception as e:
    print(f"Caught generic exception: {type(e).__name__}: {e}")

# 4. else block
separator("Else block")
try:
    result = 10 / 2
except ZeroDivisionError:
    print("Division by zero")
else:
    print(f"Success, result = {result}")

# 5. finally block\    
separator("Finally block")
try:
    val = int("not_int")
except ValueError as e:
    print(f"ValueError: {e}")
finally:
    print("Cleanup actions always run")

# 6. Raising exceptions\    
separator("Raising exceptions")
def check_positive(n):
    if n < 0:
        raise ValueError(f"Negative value not allowed: {n}")
    return n

try:
    check_positive(-5)
except ValueError as e:
    print(f"Raised and caught: {e}")

# 7. Custom exception classes\    
separator("Custom exceptions")
class MeasurementError(Exception):
    """Exception raised for measurement failures"""
    pass

try:
    raise MeasurementError("Sensor read timeout")
except MeasurementError as e:
    print(f"Custom error: {e}")

# 8. Exception chaining (raise from)\    
separator("Exception chaining")
try:
    try:
        int("bad")
    except ValueError as e:
        raise RuntimeError("Higher-level error") from e
except RuntimeError as e:
    print(f"Chained exception: {e}")
    print(f"Original cause: {e.__cause__}")

# 9. Re-raising exceptions\    
separator("Re-raising")
try:
    try:
        [] + 5
    except TypeError as e:
        print("Handling TypeError, then re-raising")
        raise
except TypeError:
    print("Re-raised TypeError caught at outer level")

# 10. Using assert for sanity checks\    
separator("Assert statement")
def sqrt(x):
    assert x >= 0, "x must be non-negative"
    return x ** 0.5

try:
    sqrt(-1)
except AssertionError as e:
    print(f"AssertionError: {e}")

# End of error_handling examples
