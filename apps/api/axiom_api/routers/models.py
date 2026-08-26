from fastapi import APIRouter, Depends, HTTPException

from axiom_anthropic import AnthropicNotConfiguredError
from axiom_core.config import get_settings
from axiom_core.models import (
    ModelBackendError,
    ModelBackendNotFoundError,
    ModelGatewayRegistry,
    ModelMessage,
    ModelRequest,
)

from axiom_api.dependencies import get_model_gateway
from axiom_api.schemas import CompletionRequest, CompletionResponse, UsageOut

router = APIRouter(prefix="/v1/models", tags=["models"])


@router.get("")
async def list_model_backends(
    gateway: ModelGatewayRegistry = Depends(get_model_gateway),
) -> dict[str, dict[str, str]]:
    """Local-only status per registered provider — no paid API calls,
    see ModelGatewayRegistry / ModelBackend.is_configured() docstrings.
    """
    providers = {}
    for name in gateway.list_providers():
        backend = gateway.get(name)
        providers[name] = "configured" if await backend.is_configured() else "not_configured"
    return {"providers": providers}


@router.post("/complete", response_model=CompletionResponse)
async def complete(
    body: CompletionRequest,
    gateway: ModelGatewayRegistry = Depends(get_model_gateway),
) -> CompletionResponse:
    settings = get_settings()
    try:
        backend = gateway.get("anthropic")
    except ModelBackendNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    model_request = ModelRequest(
        messages=[ModelMessage(role=m.role, content=m.content) for m in body.messages],
        model=body.model or settings.anthropic_default_model,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
        system=body.system,
    )

    try:
        response = await backend.generate(model_request)
    except AnthropicNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ModelBackendError as exc:
        # The upstream provider call itself failed (rate limit, billing,
        # transient outage, ...) — a clean 502, not a raw 500 traceback.
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return CompletionResponse(
        content=response.content,
        model=response.model,
        provider=response.provider,
        usage=UsageOut(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.total_tokens,
        ),
        stop_reason=response.stop_reason,
    )
