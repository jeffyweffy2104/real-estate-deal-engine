class PipelineError(Exception):
    """Base pipeline exception."""


class ValidationError(PipelineError):
    """Schema/contract validation failure."""


class StageExecutionError(PipelineError):
    """Stage execution failure."""
