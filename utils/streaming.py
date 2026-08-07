import itertools
import logging
import time
from typing import Iterator, Iterable, List, TypeVar, Callable, Any

logger = logging.getLogger(__name__)

T = TypeVar("T")

def chunked_iterable(iterable: Iterable[T], size: int) -> Iterator[List[T]]:
    """
    Yields successive chunks of a given size from an iterable.
    Extremely memory-safe: only keeps 'size' elements in memory at a time, 
    preventing OOM errors on massive datasets.
    
    Args:
        iterable: The stream of incoming data.
        size: The maximum number of items per chunk.
        
    Yields:
        Lists of items, up to `size` in length.
    """
    if size < 1:
        raise ValueError("Chunk size must be >= 1")
        
    iterator = iter(iterable)
    while True:
        chunk = list(itertools.islice(iterator, size))
        if not chunk:
            break
        yield chunk

def track_progress(iterable: Iterable[T], log_interval: int = 10000, label: str = "Records") -> Iterator[T]:
    """
    Wraps an iterable and transparently logs processing progress based on intervals.
    
    Args:
        iterable: The stream to pass through.
        log_interval: How often (in count of items) to log progress.
        label: What to call the items in the logs.
        
    Yields:
        The unmodified items from the iterable.
    """
    count = 0
    start_time = time.time()
    
    for item in iterable:
        count += 1
        yield item
        
        if count % log_interval == 0:
            elapsed = time.time() - start_time
            rate = count / elapsed if elapsed > 0 else 0
            logger.info(f"Progress: Processed {count} {label}. Rate: {rate:.2f}/sec.")
            
    # Final summary log
    elapsed = time.time() - start_time
    rate = count / elapsed if elapsed > 0 else 0
    logger.info(f"Stream Complete: Processed {count} {label} in total. Avg Rate: {rate:.2f}/sec.")

def retry_generator(
    generator_func: Callable[..., Iterator[T]], 
    max_retries: int = 3, 
    backoff_factor: float = 2.0,
    *args: Any, 
    **kwargs: Any
) -> Iterator[T]:
    """
    Wraps a generator function with retry logic. Useful for generators that fetch data 
    over unreliable networks (e.g., streaming from HuggingFace/S3).
    
    Note: If an exception occurs, the generator restarts from the beginning.
    
    Args:
        generator_func: A callable that returns an iterator.
        max_retries: Maximum number of times to retry on failure.
        backoff_factor: Multiplier for exponential backoff sleep.
    """
    attempt = 1
    while attempt <= max_retries:
        try:
            # Re-initialize the generator
            generator = generator_func(*args, **kwargs)
            for item in generator:
                yield item
            return  # Successful completion, exit loop
            
        except Exception as e:
            logger.error(f"Error in generator {generator_func.__name__} (attempt {attempt}/{max_retries}): {e}")
            if attempt == max_retries:
                raise
            
            sleep_time = backoff_factor ** attempt
            logger.info(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
            attempt += 1

def safe_map(func: Callable[[Any], T], iterable: Iterable[Any]) -> Iterator[T]:
    """
    Applies a function to every item in an iterable, but gracefully catches, 
    logs, and drops items that raise an exception rather than crashing the whole pipeline.
    
    Args:
        func: The mapping function (e.g., normalization logic).
        iterable: The input data stream.
        
    Yields:
        Successfully mapped items.
    """
    for item in iterable:
        try:
            yield func(item)
        except Exception as e:
            logger.error(f"SafeMap: Dropped item due to mapping exception: {e}")
