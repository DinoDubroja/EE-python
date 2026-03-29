

# === Functions and Scope Syntax ===
# Demonstration of Python functions and variable scope with examples and printed results

def separator(title):
    print(f"\n=== {title} ===")

# 1. Simple function with return
separator("1. Simple function with return")
def add(a, b):
    """Return the sum of a and b"""
    return a + b
print("add(2, 3):", add(2, 3))
print("add docstring:", add.__doc__)

# 2. Default arguments
separator("2. Default arguments")
def power(base, exponent=2):
    """Raise base to exponent, default exponent=2"""
    return base ** exponent
print("power(5):", power(5))
print("power(5, 3):", power(5, 3))

# 3. Keyword arguments
separator("3. Keyword arguments")
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"
print(greet("Alice"))
print(greet(name="Bob", greeting="Hi"))

# 4. *args (variable positional arguments)
separator("4. *args (variable positional arguments)")
def sum_all(*args):
    """Return sum of all positional args"""
    total = 0
    for x in args:
        total += x
    return total
print("sum_all(1,2,3,4):", sum_all(1,2,3,4))
print("sum_all():", sum_all())

# 5. **kwargs (variable keyword arguments)
separator("5. **kwargs (variable keyword arguments)")
def print_info(**kwargs):
    """Print key-value pairs from kwargs"""
    for key, value in kwargs.items():
        print(f"{key} = {value}")
print_info(sensor="ADC", channel=1, value=3.3)

# 6. Combining args, defaults, and kwargs
separator("6. Combining args, defaults, and kwargs")
def complex_func(x, y=10, *args, scale=1.0, **kwargs):
    """Illustrates mixed argument types"""
    result = (x + y) * scale + sum(args)
    print(f"kwargs inside func: {kwargs}")
    return result
print(complex_func(1))
print(complex_func(1, 2, 3, 4, scale=2.0, mode="fast", debug=True))

# 7. Variable scope: local vs global
separator("7. Variable scope: local vs global")
var = "global"
print("Before function, var =", var)
def scope_test():
    var = "local"
    print("Inside without global, var =", var)
scope_test()
print("After function, var =", var)

def scope_test_global():
    global var
    var = "modified global"
    print("Inside with global, var =", var)
scope_test_global()
print("After modifying global, var =", var)

# 8. Nested function and closure
separator("8. Nested function and closure")
def outer(msg):
    def inner():
        return f"Inner says: {msg}"
    return inner
f = outer("Hello")
print(f())

# 9. Lambda functions
separator("Lambda function")
doubler = lambda x: x * 2
print("doubler(5):", doubler(5))
print("Anonymous lambda in map:", list(map(lambda v: v+1, [1,2,3])))

# 10. Missing return yields None\separator("Missing return => None")
def no_return(a, b):
    a + b  # no return
print("no_return(2,3):", no_return(2,3))
