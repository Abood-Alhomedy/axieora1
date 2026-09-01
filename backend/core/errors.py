class PipelineError(Exception):
    """Base class for all Pipeline-related errors in the Agent Factory."""
    def __init__(self, message: str, raw_output: dict = None):
        super().__init__(message)
        self.raw_output_available = raw_output is not None
        self.raw_output = raw_output

class LLMError(PipelineError):
    """Raised when the LLM service fails or returns unexpectedly formatted responses."""
    pass

class ValidationError(PipelineError):
    """Raised when validation (Design or Code) fails strictly."""
    pass

class RegistryError(PipelineError):
    """Raised when required tools/skills/architectures are missing from the registry."""
    pass

class ArchitectureError(PipelineError):
    """Raised when an architecture contract is violated (e.g. missing required workers)."""
    pass

class GenerationError(PipelineError):
    """Raised when the Jinja template rendering or file writing fails."""
    pass

class EvaluationError(PipelineError):
    """Raised when the post-generation evaluation fails logic or syntax checks."""
    pass
