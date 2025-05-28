from pydantic import BaseModel
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class Request(BaseModel):
    text: str

class State(TypedDict):
    messages:Annotated[list,add_messages]

class ChatRequest(BaseModel):
    text: str