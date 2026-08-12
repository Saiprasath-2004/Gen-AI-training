import httpx

def fetch_data(url: str):

    try:

        response = httpx.get(
            url,
            timeout=5
        )

        print("STATUS:", response.status_code)
        print("CONTENT TYPE:", response.headers.get("content-type"))
        print("TEXT:", response.text[:500])

        response.raise_for_status()
        if response.status_code == 204:
            return []


        return response.json()
    except httpx.TimeoutException:

        print(
            f"Timeout while calling {url}"
        )

        return None

    except httpx.HTTPStatusError as exc:

        print(
            f"HTTP Error: {exc.response.status_code}"
        )
        return None

    except Exception as exc:
        print(
            f"Unexpected Error: {exc}"
        )

        return None

def timeout_demo():

    try: 

        response = httpx.get(
            "https://api.github.com",
            timeout=0.00001
        )   

        return response.json()

    except  httpx.TimeoutException:

        print("Timeout occured")

        return None