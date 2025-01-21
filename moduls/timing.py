""" timing.py 

This module provides a decorator to measure the time taken by a function.

@Author: Philipp Eilmann
"""

from functools import wraps

def time_it(func):
    """Decorator to measure the time taken by a function.
    
    Usage:
    ------
    @time_it
    def my_function():
        pass
    
    Args:
        func (callable): The function to measure the time taken by.

    Returns:
        callable: The wrapper function.
    """
    import time
    @wraps(func)
    def wrapper(*args,**kwargs):
        start = time.time()
        result = func(*args,**kwargs)
        print(f'time taken by {func.__name__} is {time.time()-start }')
        return result
    return wrapper