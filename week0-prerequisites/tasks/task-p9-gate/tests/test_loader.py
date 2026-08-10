import json
from pathlib import Path

from token_reporter.loader import load_messages


def test_load_messages(tmp_path):

    sample = [
        {
            "role": "USER",
            "content": "Hello",
            "tokens": 100
        }
    ]

    file = tmp_path / "messages.json"

    file.write_text(
        json.dumps(sample)
    )

    messages = load_messages(file)

    assert len(messages) == 1
    assert messages[0].tokens == 100