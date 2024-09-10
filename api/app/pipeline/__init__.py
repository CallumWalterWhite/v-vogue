from abc import ABC, abstractmethod
import logging
from typing import Awaitable
from app.models import OutboundMessage, PipelineState
from app.core.deps import get_session
from sqlmodel import select, Session
from app.service.message_service import MessageService, get_message_service
import uuid
import json

class PipelineMessageFactory():
    @staticmethod
    def create_message(pipeline_state: PipelineState, process_message_type:str, complete_message_type:str, failure_message_type:str) -> OutboundMessage:
        pipeline_parameter = json.loads(pipeline_state.pipeline_parameters)
        message = {"pipeline_id": str(pipeline_state.pipeline_id), "state": pipeline_state.state, "has_error": pipeline_state.has_error, "parameters": pipeline_parameter}
        if pipeline_state.has_error:
            return OutboundMessage(content=json.dumps(message), message_type=failure_message_type, correlation_id=pipeline_parameter["correlation_id"])
        if pipeline_state.has_completed:
            return OutboundMessage(content=json.dumps(message), message_type=complete_message_type, correlation_id=pipeline_parameter["correlation_id"])
        return OutboundMessage(content=json.dumps(message), message_type=process_message_type, correlation_id=pipeline_parameter["correlation_id"])

class Pipeline(ABC):    
    def __init__(self):
        self.__session: Session = get_session()
        self.__message_service: MessageService = get_message_service(self.__session)
        self.__logger = logging.getLogger(__name__)
        
    def create_new_state(self, pipeline_parameter: dict) -> str:
        """Create a new pipeline state in the database."""
        json_pipeline_parameter = json.dumps(pipeline_parameter)
        if not pipeline_parameter:
            raise ValueError("pipeline_parameter cannot be empty")
        if len(json_pipeline_parameter) > 255:
            raise ValueError("pipeline_parameter cannot be more than 255 characters")
        pipeline_state = PipelineState(state=0, pipeline_parameters=json_pipeline_parameter)
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

    @abstractmethod
    def get_process_message_type(self) -> str:
        pass

    @abstractmethod
    def get_complete_message_type(self) -> str:
        pass

    @abstractmethod
    def get_failure_message_type(self) -> str:
        pass

    async def process_message(self, pipeline_id: str, parameter: dict) -> None:
        """
        Trigger the pipeline to execute the next function based on the message.
        The message could be an event to move the pipeline forward.
        """
        state: PipelineState = self.get_state(pipeline_id)
        self.__logger.info(f"Processing message for pipeline {pipeline_id}")
        if state:
            graph = self.process_graph()
            self.__logger.info(f"Processing state {state.state} for pipeline {pipeline_id}")
            func_pipeline: Awaitable = graph[state.state]
            self.__logger.info(f"Processing function {func_pipeline} for pipeline {pipeline_id}")
            try:
                next_state = await func_pipeline(parameter)
                self.update_state(pipeline_id, next_state)
            except Exception as e:
                self.update_state(pipeline_id, -1, str(e))
        self.create_message(pipeline_id)
        
    def complete_state(self, pipeline_id: str) -> None:
        state_record = self.get_state(pipeline_id)
        if state_record:
            state_record.has_completed = True
            self.__session.add(state_record)
            self.__session.commit()

    def create_message(self, pipeline_id: str):
        state_record = self.get_state(pipeline_id)
        if state_record:
            message:OutboundMessage = PipelineMessageFactory.create_message(state_record, self.get_process_message_type(), self.get_complete_message_type(), self.get_failure_message_type())
            self.__message_service.create_message(message)