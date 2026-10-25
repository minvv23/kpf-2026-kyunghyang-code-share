"""파이프라인 예외."""


class PipelineError(Exception):
    """파이프라인 공통 예외."""


class ValidationError(PipelineError):
    """입력 데이터 형식 오류."""

    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or []

    def __str__(self):
        head = super().__str__()
        if not self.errors:
            return head
        more = f" 외 {len(self.errors) - 5}건" if len(self.errors) > 5 else ""
        return f"{head}: " + "; ".join(self.errors[:5]) + more


class StorageError(PipelineError):
    """저장소 읽기/쓰기 오류."""


class ExtractionError(PipelineError):
    """속성 추출 오류."""


class ModelError(PipelineError):
    """모델 학습·예측 오류."""
