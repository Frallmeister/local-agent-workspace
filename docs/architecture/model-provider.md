# Model-provider boundary (M2-01)

Implemented for [issue #12](https://github.com/Frallmeister/local-agent-workspace/issues/12).
This increment supplies an in-process scripted model, not live inference or agent execution.

## Interface assessment and decision

The [LangChain chat-model interface](https://docs.langchain.com/oss/python/langchain/models)
already provides message inputs, assistant outputs, tool calls, usage metadata and
provider integrations suitable for future LangGraph nodes. `BaseChatModel`,
`BaseMessage` and `AIMessage` cover the M2 invocation contract. `AIMessage.tool_calls`
contains tool names, argument dictionaries and optional call IDs;
`invalid_tool_calls` represents parsing failures. We retain these types directly.

A custom provider protocol would duplicate those messages, conversion code and
invocation semantics. Instead, `local_agent_workspace.models.ModelProvider` is
the single application entry point: a thin boundary around `BaseChatModel` that
adds application configuration validation, declared capability checks, response
validation, privacy defaults and normalized errors. There is no parallel custom
message protocol. Only `langchain-core` is added; orchestration and provider SDKs
are deferred. Existing generic fakes do not cover the complete finite script/error
scenarios here, so `ScriptedChatModel` implements the standard `_generate`
extension point with a small, non-cycling script.

Framework methods such as `bind_tools` and `with_structured_output`, or optional
model profiles, do not prove that a selected model reliably supports a workflow.
M2-01 checks an explicit supported-model declaration. Live tool-call reliability
still requires separate model-specific evaluation. Native structured output,
streaming and tool-schema binding are not exposed by this minimum synchronous
boundary. A caller requesting an unknown capability is rejected; future features
must extend this declaration and tests before use.

## Configuration and integration

Configuration is passed explicitly as a mapping; nothing reads environment
variables to choose a provider. Both keys are required. The only provider is
`scripted`, with models `text-v1` (text only) and `tools-v1` (text and tool calls).
Unknown providers/models, missing values, or extra fields fail closed. There are
no connection options, credentials, endpoints, generation parameters or fallback
providers because none are consumed by this implementation. This test-only
selection does not change ADR-0004's intended local Ollama default for live inference.

```python
from langchain_core.messages import AIMessage, HumanMessage
from local_agent_workspace.models import Capability, create_provider

provider = create_provider(
    {"provider": "scripted", "model": "tools-v1"},
    required=frozenset({Capability.TOOL_CALLING}),
    script=[
        AIMessage(content="Ready"),
        AIMessage(
            content="",
            tool_calls=[
                {"name": "example_read", "args": {"path": "sample.txt"}, "id": "call-1"}
            ],
        ),
    ],
)
messages = [HumanMessage(content="Use synthetic data")]
reply = provider.invoke(messages)
request = provider.invoke([*messages, reply])
assert request.tool_calls[0]["name"] == "example_read"
```

Use `required` at construction to reject an unsupported workflow before client
construction, or on `invoke` before the script is consumed. `config` records
provider/model selection; `capabilities` is an immutable set of declarations.
Tool-call output is untrusted data, never permission to execute a tool. Future
orchestration must dispatch through the policy gateway (ADR-0003).

Each script element is an `AIMessage`, a mapping validated as an `AIMessage` at
invocation, or an exception to simulate failure. A failed response consumes one
element; invalid input or missing capability consumes none. Exhaustion raises an
inference error, with no retry or cycling. Replies are copied, and absent message
IDs become stable `scripted-N` IDs. Optional tool-call IDs remain optional;
provided IDs must be nonempty and unique within the reply. Empty tool names,
non-dictionary arguments, invalid tool calls, incompatible message roles and
undeclared tool output are rejected. Each provider owns one sequential script;
create separate instances for independent callers. Concurrency is out of scope.

## Errors and privacy

`ModelError.category` is stable; its message contains only the category:

| Category | Meaning |
| --- | --- |
| `configuration` | Missing, unknown or invalid selection/options |
| `unsupported_capability` | Required support is not declared |
| `validation` | Invalid message input or malformed/incompatible model response |
| `transport` | `TimeoutError` or `ConnectionError` from inference |
| `inference` | Other provider failures, including script exhaustion |

Raw exception text and exception chaining are omitted. There is no payload
logging, caller callback configuration, or remote fallback. Ambient LangSmith
tracing is disabled during invocation. Future provider integrations must map
their SDK-specific transport errors, preserve these privacy defaults and declare
capabilities for the selected model; no production adapter is verified here.
Do not log messages, scripts or local variable dumps from tracebacks. Model
outputs can themselves contain private data and must be handled accordingly.

## Verification scope

`tests/backend/test_models.py` checks ordered text/tool replies, configuration
rejection before construction, capability rejection before invocation, malformed
responses, failure categories, exhaustion, isolated scripts and safe default logs.
Network connection attempts fail these tests, including with ambient tracing enabled.
Existing health tests remain independent of model setup.

Coverage: FR-002–004 and FR-014 (contract only), NFR-003, NFR-005, NFR-008;
SEC-004, SEC-007–008, SEC-011; ADR-0001/0004; T-01, T-06, T-11.
Fake tests establish deterministic boundary behavior, not real model quality,
local inference, authorization enforcement, or successful live tool calling.
Ollama belongs to M2-02; agent execution belongs to later issues. No API,
filesystem tools, persistence or plugin infrastructure is added.
