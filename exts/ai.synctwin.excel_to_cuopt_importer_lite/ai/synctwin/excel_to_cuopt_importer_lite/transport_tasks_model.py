from pydantic import BaseModel 
from typing import List 

class TransportTaskTimeWindowModel(BaseModel):
    from_ts:int=0
    to_ts:int=0

class TransportLocationModel(BaseModel):
    id:int = -1
    path:str = ""

class TransportTaskModel(BaseModel):
    location_id:int = ""    
    demand:int = 1
    time_window : TransportTaskTimeWindowModel = TransportTaskTimeWindowModel()
    service_time = 0    

class TransportTasksModel(BaseModel):
    locations:List[TransportLocationModel] = []
    tasks:List[TransportTaskModel] = []
