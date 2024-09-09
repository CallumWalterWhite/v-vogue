from abc import ABC, abstractmethod
from typing import Awaitable, Callable
from app.models import PipelineState
from app.core.deps import get_session
from sqlmodel import select, Session
from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager
import uuid

class Pipeline(ABC):    
    def __init__(self):
        self.__session: Session = get_session()
        self.__storage_manager: StorageManager = get_storage_manager()
        
    def create_new_state(self) -> str:
        """Create a new pipeline state in the database."""
        pipeline_state = PipelineState(state=0)
        self.__session.add(pipeline_state)
        self.__session.flush()
        self.__session.commit()
        pipeline_state_id = str(pipeline_state.pipeline_id)
        return pipeline_state_id
    
    def get_state(self, pipeline_id: str) -> PipelineState | None:
        statement = select(PipelineState).where(PipelineState.pipeline_id == uuid.UUID(pipeline_id))
        pipeline_state: PipelineState = self.__session.exec(statement).one()
        """Retrieve the current state of the pipeline from the database."""
        if pipeline_state:
            return pipeline_state
        return None

    def update_state(self, pipeline_id: str, new_state: int, error_message: str | None = None) -> None:
        """Update the pipeline state in the database."""
        state_record = self.get_state(pipeline_id)
        if state_record:
            state_record.state = new_state
            if error_message:
                state_record.has_error = True
                state_record.error_message = error_message
            self.__session.add(state_record)
            self.__session.commit()
        
        
    @abstractmethod    
    def process_graph(self) -> dict[int|Awaitable]:
        pass

    async def process_message(self, pipeline_id: str, parameter: dict) -> None:
        """
        Trigger the pipeline to execute the next function based on the message.
        The message could be an event to move the pipeline forward.
        """
        state: PipelineState = self.get_state(pipeline_id)
        if state:
            graph = self.process_graph()
            print(graph)
            print(state.state)
            func_pipeline = graph[state.state]
            try:
                next_state = await func_pipeline.__call__(parameter)
                self.update_state(pipeline_id, next_state)
            except Exception as e:
                self.update_state(pipeline_id, -1, str(e))
        
    def complete_state(self, pipeline_id: str) -> None:
        state_record = self.get_state(pipeline_id)
        if state_record:
            state_record.has_completed = True
            self.__session.add(state_record)
            self.__session.commit()