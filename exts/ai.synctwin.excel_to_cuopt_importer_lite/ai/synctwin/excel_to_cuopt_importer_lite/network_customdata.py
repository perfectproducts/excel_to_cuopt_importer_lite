from pxr import Usd, Tf, UsdGeom
from .network_model import *

def _node_prim_path(network_path, node)->str:
    return f"{network_path}/nodes/{Tf.MakeValidIdentifier(node.node_type)}/{Tf.MakeValidIdentifier(node.name)}"
def _edge_prim_path(network_path, edge)->str:
    return f"{network_path}/edges/_{edge.from_node_idx}_{edge.to_node_idx}"
def _toVec3f(pos3d:Location3d)->Gf.Vec3f:
    return Gf.Vec3f(pos3d.x, pos3d.y, pos3d.z)

class NetworkModelCustomData: 
    
    ROOT_PATH = "/World/network"

    def write(self, stage:Usd.Stage, model:NetworkModel):
         
        network_path = NetworkModelCustomData.ROOT_PATH
        network_prim = stage.DefinePrim(network_path)
        nodes = []
        network_prim.SetCustomDataByKey("mfgstd:schema", "Network#1.0.0" ) 
            
        for node in model.nodes:
            node_prim = stage.DefinePrim(_node_prim_path(network_path, node), "Xform")
            xf = UsdGeom.Xformable(node_prim)    
            xf.ClearXformOpOrder()
            p = node.position
            xf.AddTranslateOp().Set(Gf.Vec3f(p.x, p.y, p.z))
            node_prim.SetCustomDataByKey("mfgstd:schema", "NetworkNode#1.0.0" ) 
            node_prim.SetCustomDataByKey("mfgstd:properties:name", node.name ) 
            node_prim.SetCustomDataByKey("mfgstd:properties:node_type", node.node_type )             
            nodes.append(node)


        for edge in model.edges:
            edge_prim_path = _edge_prim_path(network_path, edge)
            edge_prim = stage.DefinePrim(edge_prim_path, "Xform")
            edge_prim.SetCustomDataByKey("mfgstd:schema", "NetworkEdge#1.0.0" ) 
            edge_prim.SetCustomDataByKey("mfgstd:properties:weight", edge.weight ) 
            edge_prim.SetCustomDataByKey("mfgstd:properties:weight_back", edge.weight_back ) 
            nodes_rel = edge_prim.CreateRelationship("from_to")             
            nodes_rel.SetTargets([
                _node_prim_path(network_path, nodes[edge.from_node_idx]),
                _node_prim_path(network_path, nodes[edge.to_node_idx])
                ])

    def read(self, stage) -> NetworkModel:
        print("read")
        network = NetworkModel()
        network_path =NetworkModelCustomData.ROOT_PATH
        network_prim = stage.GetPrimAtPath(network_path)
        schema = network_prim.GetCustomDataByKey("mfgstd:schema")

        nodes_path = f"{network_path}/nodes"
        nodes_prim = stage.GetPrimAtPath(nodes_path)
        node_idx_by_path = {}

        for node_type_prim in nodes_prim.GetChildren():
            type = node_type_prim.GetName()
            idx = 0
            for node_prim in node_type_prim.GetChildren():
                xf = UsdGeom.Xformable(node_prim)    
                name = str(node_prim.GetCustomDataByKey("mfgstd:properties:name"))
                node_type = str(node_prim.GetCustomDataByKey("mfgstd:properties:node_type"))
                
                node_idx_by_path[node_prim.GetPath()]=idx
                pos = xf.GetLocalTransformation().Transform(Gf.Vec3f())                
                node = NetworkNodeModel(
                    name = name,
                    node_type = node_type,
                    position=Location3d(x=pos[0],y=pos[1],z=pos[2]) 

                    ) 
                network.nodes.append(node)
                idx += 1 
        edges_path = f"{network_path}/edges"
        edges_prim = stage.GetPrimAtPath(edges_path)                     
        for edge_prim in edges_prim.GetChildren():
            weight = edge_prim.GetCustomDataByKey("mfgstd:properties:weight") 
            weight_back= edge_prim.GetCustomDataByKey("mfgstd:properties:weight_back" ) 
            nodes_rel = edge_prim.GetRelationship("from_to")             
            tgts = nodes_rel.GetTargets()
            
            from_idx = node_idx_by_path[tgts[0]]
            to_idx = node_idx_by_path[tgts[1]]
            edge = NetworkEdgeModel(from_node_idx=from_idx, to_node_idx=to_idx, weight=weight, weight_back = weight_back)
            network.edges.append(edge)
        return network


