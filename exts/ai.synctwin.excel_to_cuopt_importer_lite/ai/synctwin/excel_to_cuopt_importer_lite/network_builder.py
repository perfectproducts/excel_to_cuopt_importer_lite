from .geo_utils import GeoUtils
from pxr import Gf, UsdGeom, Usd, Sdf, UsdShade, Vt
import json 
from types import SimpleNamespace
from pxr import Tf
import networkx as nx
import json 
from types import SimpleNamespace

class NetworkBuilder:

    def __init__(self) -> None:        
        self._stop_radius = 0.75
        self._stop_height = 0.5 
        self._waypoint_radius = 0.25
        self._edge_radius = 0.20
    
    def read_graph_from_usd(self, path) -> nx.Graph: 
        print(f"read graph from usd {path}")
        graph =  nx.Graph()
        stage = Usd.Stage.Open(path)
       
        node_idx = 1
        
        node_idx_by_prim= {}
        for node in stage.Traverse(): 
            curr_path =node.GetPath()
            
            if not node.HasCustomDataKey("ipo_type"):
                continue
            ipo_type = node.GetCustomDataByKey("ipo_type")
            
            ipo_id = node.GetCustomDataByKey("ipo_id")
            ipo_name = node.GetCustomDataByKey("ipo_name")
            xform_vectors = UsdGeom.XformCommonAPI(node).GetXformVectors(Usd.TimeCode.Default())
            if ipo_type in ["WayPoint", "StopPoint"]:

                pos3d = xform_vectors[0]
                graph.add_node(node_idx,
                    position = pos3d,
                    ipo_name = ipo_name,
                    ipo_type = ipo_type,
                    ipo_id = ipo_id
                )
                node_idx_by_prim[curr_path] = node_idx 
                node_idx+=1
                #print(f"+ {node_idx} {ipo_type} {ipo_name} {ipo_id} {pos3d}")

            elif ipo_type == "Edge":
                
                targets = node.GetRelationship("from_to").GetTargets()
                if len(targets) == 2:
                    point_from_idx = node_idx_by_prim[targets[0]]
                    point_to_idx = node_idx_by_prim[targets[1]]  
                    point_from = graph.nodes[point_from_idx]
                    point_to = graph.nodes[point_to_idx]
                    edge_vector = point_to['position']-point_from['position']
                    graph.add_edge(point_from_idx, point_to_idx, weight=edge_vector.GetLength())        
                    #print(f"edge {curr_path} {a} {b}")
                    
                else:
                    print("no matching target relation")
            
        #nx.readwrite.edgelist.write_weighted_edgelist(graph, "out.json")
        print(f"result: {graph}")
        stage.Unload()
        return graph

    def create_graph_from_ipolog_json(self, json_in) -> nx.Graph:
        transport_data = json.loads(json_in, object_hook=lambda d: SimpleNamespace(**d))
        graph =  nx.Graph()
        network = transport_data.network
        node_idx = 1
        node_idx_by_ipoid = {}  
        for waypoint in network.waypoints: 
            pos = waypoint.position 
            
            pos3d = Gf.Vec3f(pos[0], pos[1], pos[2])
            node = graph.add_node(node_idx,
                position = pos3d,
                ipo_name = waypoint.name,
                ipo_type = "StopPoint" if waypoint.is_stop else "WayPoint",
                ipo_id = waypoint.id)
            node_idx_by_ipoid[waypoint.id] = node_idx
            node_idx = node_idx + 1 
            
        for connection in network.connections: 
            if connection.point_from.ref in node_idx_by_ipoid:
                point_from_idx = node_idx_by_ipoid[connection.point_from.ref]    
            else:
                print(f"didnt find {connection.point_from.ref}" )
            if connection.point_to.ref in node_idx_by_ipoid:
                point_to_idx = node_idx_by_ipoid[connection.point_to.ref]    
            else:
                print(f"didnt find {connection.point_from.ref}" )
            point_from = graph.nodes[point_from_idx]
            point_to = graph.nodes[point_to_idx]
            edge_vector = point_to['position']-point_from['position']
            graph.add_edge(point_from_idx, point_to_idx, weight=edge_vector.GetLength())        
        return graph    

    def create_networkstage_from_graph(self, graph : nx.Graph, path : str) -> str:
        print("create networkstage from graph...")  
        gb = GeoUtils()
        
        stage = gb.open_or_create_stage(path, True)
        if stage is None:
            
            return ""
                    
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z) 

        prim = stage.GetPrimAtPath("/World")
        
        
        point_mat = gb.create_material("/World", "point_material", (0, 0, 1))
        stop_mat = gb.create_material("/World", "stop_material", (1.0, 1.0, 0.0))
        edge_mat = gb.create_material("/World", "edge_material", (0.2, 0.2, 0.2))
        route_mat = gb.create_material("/World", "route_material", (1, 0, 0)) 
        prim_by_node_id = {}
        for node_id in graph.nodes:
            node = graph.nodes[node_id]
            ipo_name = node['ipo_name']
            ipo_type = node['ipo_type']
            ipo_id = node['ipo_id']
            position = node['position']
            prim_name = Tf.MakeValidIdentifier(ipo_name)
            
            if ipo_type == "StopPoint":
                prim_path = f"/World/network/stops/{prim_name}"
                prim_by_node_id[node_id] = prim_path
                node_prim = stage.DefinePrim(prim_path,'Xform')
                mesh_prim = stage.DefinePrim(f"{prim_path}/mesh", "Cylinder")
                mesh_prim.GetAttribute("radius").Set(self._stop_radius)
                mesh_prim.GetAttribute("height").Set(self._stop_height)
                
                UsdShade.MaterialBindingAPI(mesh_prim).Bind(stop_mat)
            else:
                prim_path = f"/World/network/waypoints/{prim_name}"
                prim_by_node_id[node_id] = prim_path
                node_prim = stage.DefinePrim(prim_path, 'Xform')
                mesh_prim = stage.DefinePrim(f"{prim_path}/mesh", "Sphere")
                mesh_prim.GetAttribute("radius").Set(self._waypoint_radius)
                UsdShade.MaterialBindingAPI(mesh_prim).Bind(point_mat)
            
            node_prim.SetCustomDataByKey("ipo_type", ipo_type)             
            node_prim.SetCustomDataByKey("ipo_name", ipo_name) 
            node_prim.SetCustomDataByKey("ipo_id", ipo_id)
            node['prim'] = node_prim

            xf = UsdGeom.Xformable(node_prim)    
            xf.ClearXformOpOrder()
            xf.AddTranslateOp().Set(position)        

        for a,b in graph.edges:
            node_a = graph.nodes[a]    
            node_b = graph.nodes[b]    
            edge_prim_path = f"/World/network/edges/_{a}_{b}"            
            edge_prim = stage.DefinePrim(edge_prim_path, "Xform")
            edge_mesh_prim = stage.DefinePrim(f"{edge_prim_path}/mesh", "Cylinder")
            edge_mesh_prim.GetAttribute("radius").Set(self._edge_radius)
            edge_vector = node_b['position'] - node_a['position']
            edge_mesh_prim.GetAttribute("height").Set(edge_vector.GetLength())

            edge_prim.SetCustomDataByKey("ipo_type", "Edge") 
            nodes_rel = edge_prim.CreateRelationship("from_to")

            path_a= prim_by_node_id[a]
            path_b= prim_by_node_id[b] 
            nodes_rel.SetTargets([path_a, path_b])
   
            xf = UsdGeom.Xformable(edge_prim)
            xf.ClearXformOpOrder ()
            xf.AddTranslateOp().Set(node_a['position'] + edge_vector*0.5)
            n = edge_vector.GetNormalized()
            r = Gf.Rotation(Gf.Vec3d(0,0,1), Gf.Vec3d(n[0],n[1],n[2]))
            
            xf.AddOrientOp(UsdGeom.XformOp.PrecisionDouble).Set(r.GetQuat())
            UsdShade.MaterialBindingAPI(edge_prim).Bind(edge_mat)               
        
        stage.GetRootLayer().Save()
        print(f"written to {path}")
        return path 