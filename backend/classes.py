from pydantic import BaseModel
from typing import Optional


class UserModel(BaseModel):
    usern: str
    pas: str
    id: str
  
class UserModelReg(BaseModel):
    usern: str
    pas: str  

class UserModelUpdate(BaseModel):
    usern: str
    newusern: str
    newpas: str
    
class TokenModel(BaseModel):
    token: str

class LaunchersModel(BaseModel):
    steam_id:  Optional[str] = None
    epicgames_id: Optional[str] = None
    

class SteamModel(BaseModel):
    steam_id: str
    id: str
    