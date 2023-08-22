
from pydantic import BaseModel


class Auth(BaseModel):
    api_key: str
    api_secret: str

class Config(BaseModel):
    auth: Auth
