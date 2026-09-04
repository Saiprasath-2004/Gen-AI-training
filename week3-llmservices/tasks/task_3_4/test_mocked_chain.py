import pytest
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

@tool
def dummy_tool(query: str) -> str:
    """A dummy lookup tool."""
    return f"Result for {query}"

# 1. Test standard model output response
def test_chain_output_parsing():
    mock_model = MagicMock()
    mock_model.invoke.return_value = AIMessage(content="PostgreSQL is an open source RDBMS.")
    response = mock_model.invoke([HumanMessage(content="What is Postgres?")])
    assert "open source RDBMS" in response.content

# 2. Test tool call generation mock
def test_mock_tool_calling():
    mock_model = MagicMock()
    mock_model.invoke.return_value = AIMessage(
        content="",
        tool_calls=[{"name": "dummy_tool", "args": {"query": "indexing"}, "id": "call_123"}]
    )
    response = mock_model.invoke([HumanMessage(content="Check index")])
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0]["name"] == "dummy_tool"

# 3. Test mock refusal guardrail
def test_mock_refusal_guardrail():
    mock_model = MagicMock()
    mock_model.invoke.return_value = AIMessage(content="Write operations like DROP are strictly forbidden.")
    response = mock_model.invoke([HumanMessage(content="DROP TABLE users;")])
    assert "forbidden" in response.content.lower()

# 4. Direct local tool execution without network overhead
def test_tool_execution_directly():
    result = dummy_tool.invoke({"query": "PostgreSQL"})
    assert result == "Result for PostgreSQL"