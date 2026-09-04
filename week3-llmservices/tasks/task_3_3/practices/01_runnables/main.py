from langchain_core.runnables import RunnableLambda 



def clean_text(text):
    return text.strip()

def upper_case(text):
    return text.upper()

def add_prefix(text):
    return f"Result: {text}"

clean_runnable = RunnableLambda(clean_text)
upper_runnable = RunnableLambda(upper_case)
prefix_runnable = RunnableLambda(add_prefix)

chain = (
     clean_runnable
    | upper_runnable
    | prefix_runnable

)



result = chain.invoke("   langchain is interesting   ")



print(result)