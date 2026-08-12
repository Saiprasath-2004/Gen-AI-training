import time
import httpx


def fetch_with_retry(url: str):

    wait = 1

    for attempt in range(3):

        try:

            response = httpx.get(
                url,
                timeout=2
            )

            response.raise_for_status()

            return response.json()

        except Exception:

            print(
                f"Attempt {attempt + 1} failed"
            )

            print(
                f"Waiting {wait} seconds"
            )

            time.sleep(wait)

            wait *= 2

    return None