import time
from botocore.exceptions import ClientError

def retry_with_backoff(max_retries=20, initial_backoff=1, backoff_multiplier=4):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            backoff = initial_backoff

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    print(e)
                    if e.response['Error']['Code'] in ['ResourceConflictException', 'ResourceInUseException']:
                        if retries == max_retries - 1:
                            raise
                        wait_time = backoff * (2 ** retries)
                        print(f"Encountered {e.response['Error']['Code']}. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        retries += 1
                        backoff *= backoff_multiplier
                    else:
                        raise
            raise Exception(f"Function failed after {max_retries} retries.")

        return wrapper
    return decorator