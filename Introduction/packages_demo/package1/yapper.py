
import random
import string

def yap(letters):
    """Return a random string of length 'letters'."""
    return ''.join(random.choices(string.ascii_letters, k=letters))
        