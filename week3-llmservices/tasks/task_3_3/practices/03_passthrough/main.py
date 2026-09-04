from langchain_core.runnables import RunnablePassthrough, RunnableParallel

def get_db_context(topic):
    return f"Postgres documentation contents for {topic}"

# RunnableParallel turns the dictionary into a Runnable object
chain = RunnableParallel({
    "content": get_db_context,
    "question": RunnablePassthrough()
})

result = chain.invoke("What is PostgreSQL?")

print(result)
# Output: {'question': 'What is PostgreSQL?'}   