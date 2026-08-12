from pydantic import BaseModel

class GithubResponse(BaseModel):
    current_user_url: str
    current_user_authorizations_html_url: str


class ExchangeRateResponse(BaseModel):
    result: str
    base_code: str
    time_last_update_utc: str

class JokeResponse(BaseModel):
    type: str
    setup: str
    punchline: str
    id: int