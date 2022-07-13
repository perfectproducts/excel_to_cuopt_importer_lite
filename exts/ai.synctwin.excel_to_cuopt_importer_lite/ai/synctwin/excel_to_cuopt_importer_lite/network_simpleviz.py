from .network_model import * 
from .network_customdata import _node_prim_path, _edge_prim_path, _toVec3f
from .geo_utils import GeoUtils
from pxr import UsdShade, UsdGeom 
class NetworkSimpleViz:
    def __init__(self):
        self.stop_radius = 0.75
        self.stop_height = 0.5 
        self.waypoint_radius = 0.25
        self.edge_radius = 0.20



    def write(self, stage, model):
        gb = GeoUtils(stage =stage)
        point_mat = gb.create_material("/World", "point_material", (0, 0, 1))
        stop_mat = gb.create_material("/World", "stop_material", (1.0, 1.0, 0.0))
        edge_mat = gb.create_material("/World", "edge_material", (0.2, 0.2, 0.2))
        route_mat = gb.create_material("/World", "route_material", (1, 0, 0)) 
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z) 
        network_path = "/World/network"
        network_prim = stage.GetPrimAtPath(network_path)
        node_by_id = {}

        for node in model.nodes:
            prim_path = _node_prim_path(network_path, node)
            #node_by_id[node.id] = node 
            node_prim = stage.GetPrimAtPath(prim_path)
            if node.node_type == "StopPoint":                
                mesh_prim = stage.DefinePrim(f"{prim_path}/mesh", "Cylinder")
                mesh_prim.GetAttribute("radius").Set(self.stop_radius)
                mesh_prim.GetAttribute("height").Set(self.stop_height)                
                UsdShade.MaterialBindingAPI(mesh_prim).Bind(stop_mat)
            else:                
                mesh_prim = stage.DefinePrim(f"{prim_path}/mesh", "Sphere")
                mesh_prim.GetAttribute("radius").Set(self.waypoint_radius)
                UsdShade.MaterialBindingAPI(mesh_prim).Bind(point_mat)

        for edge in model.edges:
            edge_prim_path = _edge_prim_path(network_path, edge)
            edge_prim = stage.GetPrimAtPath(edge_prim_path)
            edge_mesh_prim = stage.DefinePrim(f"{edge_prim_path}/mesh", "Cylinder")
            point_from = _toVec3f(model.nodes[edge.from_node_idx].position)
            point_to = _toVec3f(model.nodes[edge.to_node_idx].position)
            edge_vector = point_to-point_from
            
            edge_mesh_prim.GetAttribute("radius").Set(self.edge_radius)
            edge_mesh_prim.GetAttribute("height").Set(edge_vector.GetLength())
            xf = UsdGeom.Xformable(edge_prim)
            xf.ClearXformOpOrder ()
            xf.AddTranslateOp().Set(point_from + edge_vector*0.5)
            n = edge_vector.GetNormalized()
            r = Gf.Rotation(Gf.Vec3d(0,0,1), Gf.Vec3d(n[0],n[1],n[2]))            
            xf.AddOrientOp(UsdGeom.XformOp.PrecisionDouble).Set(r.GetQuat())
            UsdShade.MaterialBindingAPI(edge_prim).Bind(edge_mat)           
            

         



