from abc import ABC, abstractmethod
from typing import Dict, Type
from sqlmodel import select
from app.models import FileUploadPipeline, PipelineState, VitonUploadPipeline
from app.core.deps import SessionDep
import uuid

def get_status_image_service(session:SessionDep):
    return StatusImageService(session)

class StatusProgressionCalculation(ABC):
    @abstractmethod
    def calculate_progression(self, state: int) -> int:
        pass


class GarmentStatusProgressionCalculation(StatusProgressionCalculation):
    _progress_map: Dict[int, int] = {
        0: 50,
        1: 100
    }

    def calculate_progression(self, state: int) -> int:
        progression = self._progress_map.get(state, -1)
        if progression == -1:
            print(f"GarmentStatusProgressionCalculation: Invalid state {state}")
        return progression


class ModelStatusProgressionCalculation(StatusProgressionCalculation):
    _progress_map: Dict[int, int] = {
        0: 20,
        1: 40,
        2: 60,
        3: 80,
        4: 100
    }

    def calculate_progression(self, state: int) -> int:
        progression = self._progress_map.get(state, -1)
        if progression == -1:
            print(f"ModelStatusProgressionCalculation: Invalid state {state}")
        return progression
    
class VitonStatusProgressionCalculation(StatusProgressionCalculation):
    _progress_map: Dict[int, int] = {
        0: 50,
        1: 100
    }

    def calculate_progression(self, state: int) -> int:
        progression = self._progress_map.get(state, -1)
        if progression == -1:
            print(f"VitonStatusProgressionCalculation: Invalid state {state}")
        return progression


class StatusProgressionCalculationFactory:
    _factory_map: Dict[str, Type[StatusProgressionCalculation]] = {
        "garment": GarmentStatusProgressionCalculation,
        "model": ModelStatusProgressionCalculation,
        "viton": VitonStatusProgressionCalculation
    }

    @staticmethod
    def create_calculation(calculation_type: str) -> StatusProgressionCalculation:
        try:
            calculation_class = StatusProgressionCalculationFactory._factory_map[calculation_type.lower()]
            return calculation_class()
        except KeyError:
            raise ValueError(f"Invalid calculation type: '{calculation_type}'. Valid types are: {list(StatusProgressionCalculationFactory._factory_map.keys())}")

class ImageStautsDto:
    def __init__(self, file_id: str, has_completed: bool, has_error: bool, error_message: str, state: int = -1, progresison: int = -1):
        self.file_id = file_id
        self.has_completed = has_completed
        self.has_error = has_error
        self.error_message = error_message
        self.state = state
        self.progression = progresison
        
    file_id: str
    has_completed: bool
    has_error: bool
    error_message: str
    state: int
    progression: int

class StatusImageService:
    def __init__(self, session:SessionDep):
        self.session = session

    def get_image_status(self, file_id: str, file_type="file") -> ImageStautsDto:
        image_id = uuid.UUID(file_id)
        pipeline_id: uuid.UUID | None = None
        
        if file_type == "file":
            file_upload_pipeline_statement = select(FileUploadPipeline).where(FileUploadPipeline.file_upload_id == image_id)
            file_upload_pipeline: FileUploadPipeline = self.session.exec(file_upload_pipeline_statement).one_or_none()
            if file_upload_pipeline is None:
                return ImageStautsDto(file_id=file_id, has_completed=False, has_error=True, error_message="File not found")
        elif file_type == "viton":
            viton_upload_pipeline_statement = select(VitonUploadPipeline).where(VitonUploadPipeline.viton_upload_id == image_id)
            viton_upload_pipeline: VitonUploadPipeline = self.session.exec(viton_upload_pipeline_statement).one_or_none()
            if viton_upload_pipeline is None:
                return ImageStautsDto(file_id=file_id, has_completed=False, has_error=True, error_message="Viton not found")
            pipeline_id = viton_upload_pipeline.pipeline_id
        if pipeline_id is None:
            raise ValueError("Pipeline id is None")
        pipeline_state_statement = select(PipelineState).where(PipelineState.pipeline_id == pipeline_id)
        pipeline_state: PipelineState = self.session.exec(pipeline_state_statement).one_or_none()
        if pipeline_state is None:
            return ImageStautsDto(file_id=file_id, has_completed=False, has_error=True, error_message="Pipeline not found")
        progression_calculation: StatusProgressionCalculation = StatusProgressionCalculationFactory.create_calculation(pipeline_state.pipeline_type)
        progression: int = progression_calculation.calculate_progression(pipeline_state.state)
        return ImageStautsDto(
            file_id=file_id, 
            has_completed=pipeline_state.has_completed, 
            has_error=pipeline_state.has_error, 
            error_message=pipeline_state.error_message, 
            state=pipeline_state.state,
            progresison=progression)
    
    def get_viton_status(self, file_id: str) -> ImageStautsDto:
        return self.get_image_status(file_id, "viton")
    
    def get_all_completed_status(self, file_type:str = 'model') -> list[ImageStautsDto]:
        if file_type == "viton":
            file_upload_statement = select(VitonUploadPipeline)
            file_uploads: list[VitonUploadPipeline] = self.session.exec(file_upload_statement).all()
            return [self.get_image_status(file_upload.viton_upload_id, file_type) for file_upload in file_uploads]
        else:
            file_upload_statement = select(FileUploadPipeline)
            file_uploads: list[FileUploadPipeline] = self.session.exec(file_upload_statement).all()
            return [self.get_image_status(file_upload.file_upload_id, file_type) for file_upload in file_uploads]
        