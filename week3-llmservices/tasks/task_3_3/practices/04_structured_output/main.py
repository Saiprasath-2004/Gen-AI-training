import os
from dotenv import load_dotenv
from typing import List

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

class StudyAnswer(BaseModel):
    topic: str
    explanation: str
    important_concepts: List[str]
    example: str
    practice_questions: List[str]

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a senior PostgreSQL teacher. "
        "Explain concepts clearly and simply."
    ),  
    (
        "human",
        "Explain {topic}."
    ),
])

structured_model = model.with_structured_output(StudyAnswer)

chain = prompt | structured_model

result = chain.invoke({
    "topic": "PostgreSQL indexing"
})

print(result)
print()
print(result.topic)
print()
print(result.explanation)
print()
print(result.important_concepts)
print()
print(result.practice_questions)
print()
print(type(result))