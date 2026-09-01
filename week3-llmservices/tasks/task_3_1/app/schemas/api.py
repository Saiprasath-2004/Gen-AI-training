from pydantic import BaseModel , Field

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=10_000,
        description="User's natural-language request.",
    )


class ChatResponse(BaseModel):
    answer: str