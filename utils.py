import pandas as pd
import os
import functools

def cache():
    """Decorator to cache function results as CSV files."""
    cache_dir='data/cache'
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Ensure cache directory exists
            os.makedirs(cache_dir, exist_ok=True)

            # Generate cache file path based on function arguments
            cache_filename = "_".join(
                [func.__name__] + 
                ["_".join(v) for _, v in kwargs.items()]
            ) + ".csv"
            print(cache_filename)
            cache_path = os.path.join(cache_dir, cache_filename)

            # If cached file exists, return cached DataFrame
            if os.path.exists(cache_path):
                print(f"Loading cached data from {cache_path}")
                return pd.read_csv(cache_path)

            # Run function normally and cache result
            result = func(*args, **kwargs)
            if isinstance(result, pd.DataFrame):
                result.to_csv(cache_path, index=False)
                print(f"Cached result at {cache_path}")
            return result
        return wrapper
    return decorator