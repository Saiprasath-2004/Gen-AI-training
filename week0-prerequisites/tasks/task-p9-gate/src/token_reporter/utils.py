from  token_reporter.models import(
    Message,
    ProcessedMessage   
)

def process_message(
    message: Message
) -> ProcessedMessage:

    return ProcessedMessage(
        role= message.role,
        content=message.content,
        tokens=message.tokens
    )