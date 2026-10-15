import logging
import socket
import traceback

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from local_agent_workspace.models import (
    Capability,
    ErrorCategory,
    ModelError,
    create_provider,
)

CONFIG = {"provider": "scripted", "model": "tools-v1"}
TOOLS = frozenset({Capability.TOOL_CALLING})


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args, **kwargs):
        pytest.fail("Model boundary attempted network access")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)


def test_text_tool_and_successive_messages():
    request = AIMessage(
        content="",
        tool_calls=[{"name": "read", "args": {"path": "sample.txt"}, "id": "call-1"}],
    )
    provider = create_provider(
        CONFIG,
        script=[AIMessage(content="First"), request, AIMessage(content="Done")],
        required=TOOLS,
    )
    history = [HumanMessage(content="Read sample")]
    first = provider.invoke(history)
    assert first.content == "First"
    assert first.id == "scripted-1"
    history.append(first)
    second = provider.invoke(history, required=TOOLS)
    assert second.tool_calls == request.tool_calls
    history.extend(
        [second, ToolMessage(content="Synthetic result", tool_call_id="call-1")]
    )
    assert provider.invoke(history).content == "Done"
    with pytest.raises(ModelError) as error:
        provider.invoke(history)
    assert error.value.category == ErrorCategory.INFERENCE


@pytest.mark.parametrize(
    "config",
    [
        {},
        {"provider": "scripted"},
        {"model": "text-v1"},
        {"provider": "openai", "model": "text-v1"},
        {"provider": "ollama", "model": "text-v1"},
        {"provider": "scripted", "model": ""},
        {"provider": "scripted", "model": "unknown"},
        {**CONFIG, "base_url": "https://example.invalid"},
        {**CONFIG, "api_key": "secret-value"},
    ],
)
def test_invalid_configuration_never_constructs_client(config, monkeypatch):
    def deny(**kwargs):
        pytest.fail("Constructed a client for invalid configuration")

    monkeypatch.setattr("local_agent_workspace.models.ScriptedChatModel", deny)
    with pytest.raises(ModelError) as error:
        create_provider(config, script=[])
    assert error.value.category == ErrorCategory.CONFIGURATION
    assert error.value.__context__ is None


def test_capability_rejected_before_construction(monkeypatch):
    def deny(**kwargs):
        pytest.fail("Constructed an unsupported client")

    monkeypatch.setattr("local_agent_workspace.models.ScriptedChatModel", deny)
    with pytest.raises(ModelError) as error:
        create_provider({**CONFIG, "model": "text-v1"}, script=[], required=TOOLS)
    assert error.value.category == ErrorCategory.UNSUPPORTED_CAPABILITY


def test_capability_rejected_without_consuming_script():
    provider = create_provider(
        {**CONFIG, "model": "text-v1"}, script=[AIMessage(content="Still first")]
    )
    with pytest.raises(ModelError) as error:
        provider.invoke([HumanMessage(content="test")], required=TOOLS)
    assert error.value.category == ErrorCategory.UNSUPPORTED_CAPABILITY
    assert provider.invoke([HumanMessage(content="test")]).content == "Still first"


@pytest.mark.parametrize(
    "step,category",
    [
        (
            {"content": "", "tool_calls": [{"name": "read", "args": "bad", "id": "1"}]},
            ErrorCategory.VALIDATION,
        ),
        (
            {"content": "", "tool_calls": [{"name": "", "args": {}, "id": "1"}]},
            ErrorCategory.VALIDATION,
        ),
        (
            {"content": "", "invalid_tool_calls": [{"name": "read", "args": "bad"}]},
            ErrorCategory.VALIDATION,
        ),
        (
            {
                "content": "",
                "tool_calls": [
                    {"name": "read", "args": {}, "id": "1"},
                    {"name": "read", "args": {}, "id": "1"},
                ],
            },
            ErrorCategory.VALIDATION,
        ),
        (HumanMessage(content="Wrong role"), ErrorCategory.VALIDATION),
        (RuntimeError("private payload"), ErrorCategory.INFERENCE),
        (TimeoutError("private endpoint"), ErrorCategory.TRANSPORT),
        (ConnectionError("private endpoint"), ErrorCategory.TRANSPORT),
    ],
)
def test_invalid_responses_and_failures(step, category):
    provider = create_provider(CONFIG, script=[step, AIMessage(content="Next")])
    messages = [HumanMessage(content="private prompt")]
    with pytest.raises(ModelError) as error:
        provider.invoke(messages)
    assert error.value.category == category
    assert error.value.__context__ is None
    assert "private" not in "".join(traceback.format_exception(error.value))
    assert provider.invoke([HumanMessage(content="test")]).content == "Next"


def test_undeclared_tool_response_rejected():
    provider = create_provider(
        {**CONFIG, "model": "text-v1"},
        script=[
            AIMessage(content="", tool_calls=[{"name": "read", "args": {}, "id": None}])
        ],
    )
    with pytest.raises(ModelError) as error:
        provider.invoke([HumanMessage(content="test")])
    assert error.value.category == ErrorCategory.VALIDATION


def test_optional_call_identity():
    provider = create_provider(
        CONFIG,
        script=[
            AIMessage(content="", tool_calls=[{"name": "read", "args": {}, "id": None}])
        ],
    )
    assert provider.invoke([HumanMessage(content="test")]).tool_calls[0]["id"] is None


def test_default_logs_and_ambient_tracing_do_not_capture_payloads(caplog, monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGSMITH_API_KEY", "synthetic-test-key")
    caplog.set_level(logging.DEBUG)
    provider = create_provider(
        CONFIG,
        script=[
            AIMessage(
                content="SENSITIVE_REPLY",
                tool_calls=[
                    {"name": "read", "args": {"path": "SENSITIVE_PATH"}, "id": "1"}
                ],
            ),
            RuntimeError("SENSITIVE_FAILURE"),
        ],
    )
    assert provider.invoke([HumanMessage(content="SENSITIVE_PROMPT")]).tool_calls
    with pytest.raises(ModelError):
        provider.invoke([HumanMessage(content="SENSITIVE_PROMPT")])
    assert "SENSITIVE" not in caplog.text


def test_invalid_input_does_not_consume_reply():
    provider = create_provider(CONFIG, script=[AIMessage(content="Ready")])
    with pytest.raises(ModelError) as error:
        provider.invoke([])
    assert error.value.category == ErrorCategory.VALIDATION
    assert provider.invoke([HumanMessage(content="test")]).content == "Ready"


def test_scripts_are_isolated_and_repeatable():
    reply = AIMessage(content="Same")
    first = create_provider(CONFIG, script=[reply])
    second = create_provider(CONFIG, script=[reply])
    assert first.invoke([HumanMessage(content="test")]) == second.invoke(
        [HumanMessage(content="test")]
    )
    assert reply.id is None


def test_unknown_capability_is_not_advertised():
    with pytest.raises(ModelError) as error:
        create_provider(CONFIG, script=[], required=frozenset({"structured_output"}))
    assert error.value.category == ErrorCategory.UNSUPPORTED_CAPABILITY


def test_history_is_forwarded_without_rewriting(monkeypatch):
    from local_agent_workspace.models import ScriptedChatModel

    observed = []
    original = ScriptedChatModel._generate

    def record(self, messages, **kwargs):
        observed.extend(messages)
        return original(self, messages, **kwargs)

    monkeypatch.setattr(ScriptedChatModel, "_generate", record)
    history = [
        HumanMessage(content="question"),
        AIMessage(content="", tool_calls=[{"name": "read", "args": {}, "id": "1"}]),
        ToolMessage(content="result", tool_call_id="1"),
    ]
    provider = create_provider(CONFIG, script=[AIMessage(content="answer")])
    assert provider.invoke(history).content == "answer"
    assert observed == history
