class PipelineError(Exception):
    code = "pipeline_error"

    def __init__(self, message: str, *, recoverable: bool = False):
        super().__init__(message)
        self.message = message
        self.recoverable = recoverable


class RetrievalError(PipelineError):
    code = "retrieval_failed"


class GuardrailServiceError(PipelineError):
    code = "guardrail_unavailable"


class GenerationError(PipelineError):
    code = "generation_failed"


class ProviderError(GenerationError):
    def __init__(self, message: str, provider: str, *, recoverable: bool = True):
        super().__init__(f"[{provider}] {message}", recoverable=recoverable)
        self.provider = provider


def to_event(exc: PipelineError) -> dict:
    return {"type": "error", "code": exc.code, "message": exc.message}