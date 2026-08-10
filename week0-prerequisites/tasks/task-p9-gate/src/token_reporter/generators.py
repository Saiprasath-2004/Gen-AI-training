def chunk_text(
    text: str,
    chunk_size: int = 20
):
    """ 
        Yield text in chunks
    """

    for i in range(
        0,
        len(text),
        chunk_size
    ): 
        yield text[i:i + chunk_size]