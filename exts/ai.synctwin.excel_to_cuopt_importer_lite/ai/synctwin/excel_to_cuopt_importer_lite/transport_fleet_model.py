from pydantic import BaseModel 
from typing import List 

class TransportVehicleAvailabilityModel(BaseModel):
    from_ts : int =0
    to_ts : int =1000000

class TransportVehicleModel(BaseModel):
    name:str =""
    vehicle_type:str = "" 
    capacity:int = 1
    home_node_id: int = 0
    time_window:TransportVehicleAvailabilityModel = TransportVehicleAvailabilityModel()

class TransportFleetModel(BaseModel):
    vehicles:List[TransportVehicleModel] = []
