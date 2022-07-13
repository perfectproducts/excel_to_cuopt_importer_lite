from pxr import Usd, Tf, UsdGeom
from .transport_fleet_model import *

class TransportFleetModelCustomData: 
    def __init__(self) -> None:
        self._fleet_path = "/World/fleet"

    def write(self, stage:Usd.Stage, model:TransportFleetModel):

        fleet_prim = stage.DefinePrim(self._fleet_path)
        fleet_prim.SetCustomDataByKey("mfgstd:schema", "TransportFleet#1.0.0" ) 
        for vehicle in model.vehicles:
            vehicle_prim = stage.DefinePrim(f"{self._fleet_path}/vehicles/{Tf.MakeValidIdentifier(vehicle.name)}", "Xform")
            xf = UsdGeom.Xformable(vehicle_prim)    
            vehicle_prim.SetCustomDataByKey("mfgstd:schema", "TransportVehicle#1.0.0" ) 
            vehicle_prim.SetCustomDataByKey("mfgstd:properties:name", vehicle.name ) 
            vehicle_prim.SetCustomDataByKey("mfgstd:properties:vehicle_type", vehicle.vehicle_type ) 
            vehicle_prim.SetCustomDataByKey("mfgstd:properties:capacity", vehicle.capacity ) 
            vehicle_prim.SetCustomDataByKey("mfgstd:properties:home_node_id", vehicle.home_node_id ) 

    def read(self, stage:Usd.Stage )->TransportFleetModel:
        fleet = TransportFleetModel()
        
        fleet_prim = stage.GetPrimAtPath(self._fleet_path)
        schema = fleet_prim.GetCustomDataByKey("mfgstd:schema")
            
        vehicles_path = f"{self._fleet_path}/vehicles"
        vehicles_prim = stage.GetPrimAtPath(vehicles_path)
        node_id_by_path = {}
        for vehicle_prim in vehicles_prim.GetChildren():            
            
            name = str(vehicle_prim.GetCustomDataByKey("mfgstd:properties:name"))        
            vehicle_type = str(vehicle_prim.GetCustomDataByKey("mfgstd:properties:vehicle_type"))        
            capacity = int(vehicle_prim.GetCustomDataByKey("mfgstd:properties:capacity"))        
            home_node_id = int(vehicle_prim.GetCustomDataByKey("mfgstd:properties:home_node_id"))        
            
            vehicle = TransportVehicleModel(name=name, vehicle_type=vehicle_type, capacity=capacity, home_node_id=home_node_id)
            fleet.vehicles.append(vehicle)
        return fleet 

