from pydantic import BaseModel


class MessageRecieve(BaseModel):
    receiver_username: str
    text: str


class SendMessage(MessageRecieve):
    sender_username: str
