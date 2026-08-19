

class Conversation: 
    def __init__(
        self ,
        system_prompt: str,
    ) -> None:
        self.messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]


    def add_user_message(
        self,
        content: str,
    ) -> None:
        self.messages.append(
            {
                "role": "user",
                "content": content,
            }
        )

    def add_assistant_message(
        self,
        content: str,
    ) -> None:
        self.messages.append(
            {
                "role": "assistant",
                "content": content,
            }
        )

    def get_message(self) -> list[dict]:
        return self.messages