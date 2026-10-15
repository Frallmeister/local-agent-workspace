"""Thin, synchronous M2 model boundary using LangChain's message contract."""

from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Any, Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langsmith import tracing_context
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, ValidationError


class ErrorCategory(StrEnum):
    CONFIGURATION = "configuration"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    VALIDATION = "validation"
    TRANSPORT = "transport"
    INFERENCE = "inference"


class ModelError(Exception):
    """Safe public error; never carries raw provider payloads."""

    def __init__(self, category: ErrorCategory):
        self.category = category
        super().__init__(f"Model request failed: {category.value}")


class Capability(StrEnum):
    TOOL_CALLING = "tool_calling"


class ProviderConfig(BaseModel):
    """Only implemented providers/models are selectable. No connection options yet."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    provider: Literal["scripted"]
    model: Literal["text-v1", "tools-v1"]


class ScriptedChatModel(BaseChatModel):
    """Finite script, consumed once in order; no cycling, retries, or I/O.

    Dictionaries are converted on invocation so malformed responses can be tested.
    Instances belong to one caller; concurrent sharing is not supported.
    """

    script: list[Any] = Field(repr=False, exclude=True)
    _position: int = PrivateAttr(default=0)

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self._position >= len(self.script):
            raise RuntimeError("Script exhausted")
        step = self.script[self._position]
        self._position += 1
        if isinstance(step, Exception):
            raise step
        if isinstance(step, dict):
            step = AIMessage.model_validate(step)
        if not isinstance(step, AIMessage):
            raise ValueError("Expected assistant message")
        reply = step.model_copy(deep=True)
        if reply.id is None:
            reply.id = f"scripted-{self._position}"
        return ChatResult(generations=[ChatGeneration(message=reply)])


class ModelProvider:
    """Application entry point; messages remain native LangChain messages.

    Construction is through create_provider. Future integrations supply another
    BaseChatModel here, rather than introducing another invocation protocol.
    """

    def __init__(
        self,
        config: ProviderConfig,
        client: BaseChatModel,
        capabilities: frozenset[Capability],
    ):
        self.config = config
        self.capabilities = capabilities
        self._client = client

    def require(self, required: frozenset[Capability]) -> None:
        if not required <= self.capabilities:
            raise ModelError(ErrorCategory.UNSUPPORTED_CAPABILITY)

    def invoke(
        self,
        messages: Sequence[BaseMessage],
        *,
        required: frozenset[Capability] = frozenset(),
    ) -> AIMessage:
        self.require(required)
        # Do not enable ambient LangSmith tracing or accept caller callbacks that
        # could export prompts/tool arguments. No application payload logging.
        failed: ErrorCategory | None = None
        try:
            if not messages or any(not isinstance(m, BaseMessage) for m in messages):
                raise ValueError("Expected messages")
            with tracing_context(enabled=False):
                response = self._client.invoke(list(messages), config={"callbacks": []})
            self._validate_response(response)
            return response
        except ValidationError, ValueError, TypeError:
            failed = ErrorCategory.VALIDATION
        except TimeoutError, ConnectionError:
            failed = ErrorCategory.TRANSPORT
        except Exception:
            failed = ErrorCategory.INFERENCE
        # Raise outside the handler to avoid retaining a sensitive exception
        # context (even when a caller formats a complete traceback).
        raise ModelError(failed)

    def _validate_response(self, response: AIMessage) -> None:
        if not isinstance(response, AIMessage) or response.invalid_tool_calls:
            raise ValueError("Invalid assistant response")
        if response.tool_calls and Capability.TOOL_CALLING not in self.capabilities:
            raise ValueError("Undeclared tool calling")
        seen: set[str] = set()
        for call in response.tool_calls:
            if (
                not isinstance(call.get("name"), str)
                or not call["name"].strip()
                or not isinstance(call.get("args"), dict)
                or (
                    call.get("id") is not None
                    and (
                        not isinstance(call["id"], str)
                        or not call["id"].strip()
                        or call["id"] in seen
                    )
                )
            ):
                raise ValueError("Invalid tool call")
            if call.get("id") is not None:
                seen.add(call["id"])


def create_provider(
    configuration: Mapping[str, object],
    *,
    script: Sequence[AIMessage | Mapping[str, object] | Exception],
    required: frozenset[Capability] = frozenset(),
) -> ModelProvider:
    """Validate before construction; never infer a provider or perform discovery."""
    config = None
    try:
        config = ProviderConfig.model_validate(configuration)
    except ValidationError, TypeError:
        pass
    if config is None:
        raise ModelError(ErrorCategory.CONFIGURATION)
    capabilities = (
        frozenset({Capability.TOOL_CALLING})
        if config.model == "tools-v1"
        else frozenset()
    )
    if not required <= capabilities:
        raise ModelError(ErrorCategory.UNSUPPORTED_CAPABILITY)
    return ModelProvider(
        config,
        ScriptedChatModel(
            script=list(script), cache=False, callbacks=[], verbose=False
        ),
        capabilities,
    )
