from .network_model import NetworkModel, NetworkNodeModel, NetworkEdgeModel, Location3d
import pandas as pd

class NetworkExcelReaderWriter:
        
    def write(self, xls_path:str, network:NetworkModel )->bool:
        data = []
        for node in network.nodes:
            data.append([node.name, node.node_type, node.position.x, node.position.y, node.position.z])

        df = pd.DataFrame(data, columns=['Name', 'Type', 'X', 'Y', 'Z'])

        data = []
        for edge in network.edges:
            data.append([network.nodes[edge.from_node_idx].name, network.nodes[edge.to_node_idx].name, edge.weight, edge.weight_back])
        df2 = pd.DataFrame(data, columns=['From', 'To', 'Weight', 'WeightBack'])
        with pd.ExcelWriter(xls_path) as writer:
            df.to_excel(writer, sheet_name='Nodes')
            df2.to_excel(writer, sheet_name='Edges')
        return True 

    def read(self, xls_path:str)->NetworkModel:
        network= NetworkModel()
        
        df_sheet_multi = pd.read_excel(xls_path, sheet_name=['Nodes', 'Edges'])
        
        nodes_frame = df_sheet_multi['Nodes']
        node_idx_by_name = {}
        for index, row in nodes_frame.iterrows():  
            node = NetworkNodeModel(
                    name = row['Name'],
                    node_type = row['Type'],
                    position=Location3d(x=float(row['X']),y=float(row['Y']), z=float(row['Z'])) 
                    ) 
            node_idx_by_name[node.name] = len(network.nodes)
            network.nodes.append(node)
        edges_frame = df_sheet_multi['Edges']
        for index, row in edges_frame.iterrows():  
            from_idx = node_idx_by_name.get(row["From"], -1)
            to_idx= node_idx_by_name.get(row["To"], -1)
            if from_idx == -1 or to_idx == -1:
                print("## error with node idx")
                continue 
            edge = NetworkEdgeModel(from_node_idx=from_idx, to_node_idx=to_idx, weight=row['Weight'], weight_back = row['WeightBack'])
            network.edges.append(edge)

        return network