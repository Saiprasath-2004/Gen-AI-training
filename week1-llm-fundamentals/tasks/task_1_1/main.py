from api_client import (
    fetch_data,
    timeout_demo
)

from retry import (
    fetch_with_retry
)

from models import (
    GithubResponse,
    ExchangeRateResponse,
    JokeResponse
)

def main():

    print("\n===== GITHUB API =====\n")

    github_data = fetch_data(
        "https://api.github.com"
    )

    if github_data:

        github = GithubResponse.model_validate(
            github_data
        )
        print("GitHub API Success")
        print(github)
    
    print(
        "\n===== EXCHANGE RATE API =====\n"
    )

    exchange_data = fetch_data(
        "https://open.er-api.com/v6/latest/USD"
    )

    if exchange_data:
        exchange = (
            ExchangeRateResponse.model_validate(
                exchange_data
            )
        )

        print(exchange)

    print(
        "\n===== JOKE API =====\n"
    )

    joke_data = fetch_data(
        "https://official-joke-api.appspot.com/random_joke"
    )

    if joke_data:

        joke = JokeResponse.model_validate(
            joke_data
        )

        print(joke)

    print(
        "\n===== 404 DEMO =====\n"
    )

    fetch_data(
        "https://api.github.com/this-does-not-exist"
    )

    print(
        "\n===== TIMEOUT DEMO =====\n"
    )

    timeout_demo()

    print(
        "\n===== RETRY DEMO =====\n"
    )

    result = fetch_with_retry(
        "https://api.github.comddd"
    )

    print(result)


if __name__ == "__main__":
    main()