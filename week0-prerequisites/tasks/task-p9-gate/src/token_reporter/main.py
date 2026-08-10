from pathlib import Path
from time import perf_counter

from token_reporter.exceptions import InvalidJsonError
from token_reporter.loader import load_messages
from token_reporter.logger import logger
from token_reporter.report import generate_report, print_report
from token_reporter.utils import process_message

from token_reporter.generators import (
    chunk_text
)

from token_reporter.config import (
    APP_NAME,
    TOKEN_PRICE
)



def main():

    start_time = perf_counter()
    try:
        print(APP_NAME)
        print(TOKEN_PRICE)
        path = Path("../data/messages.json")

        messages = load_messages(path)

        processed_messages = []

        for message in messages:

            processed = process_message(message)

            processed_messages.append(
                processed
            )

        sample_text = (
            "This is a very long document "
            "that needs to be processed "
            "in smaller chunks."
        )

        for chunk in chunk_text(
            sample_text,
            chunk_size=15
        ):
            print(chunk)
            
        message_counter, token_totals, cost_totals = (
            generate_report(
                processed_messages
            )
        )

        print_report(
            message_counter,
            token_totals,
            cost_totals
        )

        end_time = perf_counter()

        print()
        print(
            f"Execution Time: "
            f"{end_time - start_time:.6f} seconds"
        )
    except InvalidJsonError as exc:
        logger.warning(str(exc))
        return

if __name__ == "__main__":
    main()