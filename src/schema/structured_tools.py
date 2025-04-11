from pydantic import BaseModel, Field


class Profile(BaseModel):
    character_name: str
    universe: str
    requirements: str
    user_name: str
    
    
class EvalDocuments(BaseModel):
    """
    Document evaluation class.
    The decision attribute can have a value of 'yes' or 'no' indicating the relevance of the document to the message.
    """
    decision: str = Field(description="Documents are relevant to message. This attribute can have a value of 'yes' or 'no'")
    
    
class EvalResponse(BaseModel):
    """
    Response evaluation class.
    The decision attribute can have a value of 'yes' or 'no' indicating the relevance of the response to the conversation.
    """
    decision: str = Field(description="Response is relevant to message. This attribute can have a value of 'yes' or 'no'")