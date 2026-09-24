class AiProcessingError(Exception):
    status_code = 500

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidRecordingError(AiProcessingError):
    status_code = 400


class RecordingNotFoundError(AiProcessingError):
    status_code = 404


class AudioExtractionError(AiProcessingError):
    status_code = 500


class ModelConfigurationError(AiProcessingError):
    status_code = 500


class TranscriptionError(AiProcessingError):
    status_code = 500


class DiarizationError(AiProcessingError):
    status_code = 500
