

def average(numbers):
    """Return the average of a list of numbers as an integer (rounded)."""
    if not numbers:
        return 0
    return round(sum(numbers) / len(numbers))

def increment(x, step=1):
    """Increment x by step (default 1) and return the result."""
    return x + step