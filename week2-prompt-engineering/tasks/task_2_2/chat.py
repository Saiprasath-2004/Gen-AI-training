import json
from pathlib import Path


from client import(
    ModelClient,
    parse_stream_line
)
from conversation import Conversation
from cost import CostTracker

def load_models() -> dict:
    path = Path("models.json")

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

def stream_response(
    client: ModelClient,
    conversation: Conversation,
) -> tuple[str, float]:
    """Stream one model response and return text and cost."""

    response_text = []

    usage = None

    with client.stream(
        conversation.get_message()
    ) as response:
        
        response.raise_for_status()

        print("\n Assistant: ",end="",flush=True)

        for line in response.iter_lines():
            content, chunk_usage = parse_stream_line(
                line
            )

            if content:
                print(
                    content,
                    end="",
                    flush=True
                )

                response_text.append(
                    content
                )
            if chunk_usage:
                usage  = chunk_usage

    print()

    if usage is None:
        raise RuntimeError(
            "Streaming completed without usage data"
        )

    cost = usage.get("cost") or 0.0

    return(
        "".join(response_text),
        cost,
    )

def main() -> None:
    models = load_models()

    primary_model = models[
        "primary_model"
    ]

    fallback_model = models[
        "fallback_model"
    ]

    conversation = Conversation(
        system_prompt=(
            "You are a helper AI assistant. "
            "Answer clearly and concisely."
        )
    )

    cost_tracker = CostTracker()

    primary = ModelClient(
        primary_model
    )

    fallback = ModelClient(
        fallback_model
    )

    print(
        "Conversation started."
    )

    print(
        "type 'exit' to quit." 
    )

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() == "exit":
            break

        conversation.add_user_message(
            user_input
        )

        try:
            response_text, cost = stream_response(
                primary,
                conversation
            )

        except Exception as exc:
            # print(
            #     f"\n Primary model failed: {exc}"
            # )

            # print(
            #     "Switching to fallback..."
            # )

            response_text, cost = stream_response(
                fallback,
                conversation,
            )

        conversation.add_assistant_message(
            response_text
        )

        cost_tracker.add(cost)

        print(  
            f"\nTotal conversation cost: "
            f"${cost_tracker.total():.8f}" 
        )

if __name__ == "__main__":
    main()