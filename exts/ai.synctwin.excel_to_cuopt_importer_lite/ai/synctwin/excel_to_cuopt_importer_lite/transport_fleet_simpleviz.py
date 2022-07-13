from .transport_fleet_model import * 
from .geo_utils import GeoUtils
from pxr import UsdShade, UsdGeom , Tf, Usd

class TransportFleetModelSimpleViz:
    def __init__(self) -> None:
        self._fleet_path = "/World/fleet"
        self.vehicle_radius = 1

    def write(self, stage:Usd.Stage, model:TransportFleetModel):
        gb = GeoUtils(stage =stage)
        vehicles_mat = gb.create_material("/World", "vehicle_material", (1, 0, 0))
        fleet_prim = stage.GetPrimAtPath(self._fleet_path)
        for vehicle in model.vehicles:
            prim_path = f"{self._fleet_path}/vehicles/{Tf.MakeValidIdentifier(vehicle.name)}"            
            mesh_prim = stage.DefinePrim(f"{prim_path}/mesh", "Sphere")
            mesh_prim.GetAttribute("radius").Set(float(self.vehicle_radius))
            UsdShade.MaterialBindingAPI(mesh_prim).Bind(vehicles_mat)
