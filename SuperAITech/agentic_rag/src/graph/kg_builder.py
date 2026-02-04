from neo4j import GraphDatabase
from src.graph.nodes import Node, Document, Chunk, Highlight, Role, Pic, Time
from typing import Dict, Any, List, Optional, Type
import json
class KGBuilder:
    def __init__(self,NEO4J_URI, NEO4J_USER, NEO4J_PASS):
        self.__driver = GraphDatabase.driver(NEO4J_URI, auth = (NEO4J_USER, NEO4J_PASS))
        
    def close(self):
        self.__driver.close()
        
    def existed_node(self, node:Node):
        res = None
        query = f"""
            MATCH (n:{node.label} {{uid: $uid}})
            RETURN n
        """
        with self.__driver.session() as session:
            r = session.run(query, uid=node.uid).data()
            if not r:
                res = None
            else:
                rr = [dict(record['n']) for record in r]
                if len(rr)>1:
                    print(f'[FAILED] Có nhiều hơn 1 node trùng id')
                res = rr[0]
                del res['label']
        return res
        

    def create_node(self, node:Node):
        props = node.to_dict().copy()
        # print(props)
        label = node.label
        uid = props.pop("uid",None)
        if isinstance(node, Role):
            del props['conditions']
        if isinstance(node, Pic):
            del props['desc']
        query = f"MERGE (n:{label} {{uid: $uid}})  SET n += $props"
        with self.__driver.session() as session:
            session.run(query, uid=uid, props=props)

#     def update_node(self, type, id):
#         props = node.to_dict()
#         label = node.label
#         uid = node.uid
#         query = f"MATCH (n:{label} {{uid: $uid}})  SET n += $props"
#         with self.__driver.session() as session:
#             session.run(query, uid=uid, props=props)


#     def delete_node(self, type, id):
#         props = node.to_dict().copy()
#         label = node.label
#         uid = props.pop("uid",None)
#         query = (
#             f"MATCH (n:{label} {{uid: {uid}}}) "
#             + ("DETACH DELETE n" if detach else "DELETE n")
        
#         )
#         with self.__driver.session() as session:
#             session.run(query)

    def create_relationship(self,from_node, to_nodes, rel_type: str):
        for to_node in to_nodes:
            if isinstance(from_node, Document) and isinstance(to_node, Role):
                props = {'conditions': to_node.conditions}
            elif isinstance(from_node, Document) and isinstance(to_node, Pic):
                props = {'desc': to_node.desc}
            else:
                props = {}
            query = (
                f"MATCH (a:{from_node.label} {{uid: $uid_from_node}}), (b:{to_node.label} {{uid: $uid_to_node}}) "
                f"MERGE (a)-[r:{rel_type}]->(b) "
                f"SET r += $props"
            )
            with self.__driver.session() as session:
                session.run(query, uid_from_node=from_node.uid, uid_to_node=to_node.uid, props = props)

#     def update_relationship(self,from_node, to_node, rel_type: str, props: Dict[str, Any] = None):
#         if props is None:
#             props = {}
#         query = (
#             f"MATCH (a:{from_node.label} {{uid: {from_node.uid}}})-[r:{rel_type}]->(b:{to_node.label} {{uid: {to_node.uid}}}) "
#             f"SET r += $props"
#         )
#         with self.__driver.session() as session:
#             session.run(query, props = props)
            
#     def delete_relationship(self,from_node, to_node, rel_type: str):
#         if props is None:
#             props = {}
#         query = (
#             f"MATCH (a:{from_node.label} {{uid: {from_node.uid}}})-[r:{rel_type}]->(b:{to_node.label} {{uid: {to_node.uid}}}) "
#             f"DELETE r"
#         )
#         with self.__driver.session() as session:
#             session.run(query)

    def build_graph_base(self, data_json):
        """
        ### Template json input:
        {
            "Document": {
                "uid": str, "title": str, "path": str
            },
            "Highlight": [
                {"uid":str, "text":str, "embed":list},
                {"uid":str, "text":str, "embed":list},
                ...
              ],
            "Role": {
                "uid": str {NVCT, TTS, PL, GL}, "title":str, "conditions": list[str]
            },
            "Pic": [
                {"uid": str ~ knox_id, "knox_id": str, desc: list[str], "phone":str, full_name:str, "location":str},
                {"uid": str ~ knox_id, "knox_id": str, desc: list[str], "phone":str, full_name:str, "location":str},
                ...
            ]
            "Time": {
                "uid":str, "create_at": str yyyy-MM-dd, "efficient_time": str yyyy-MM-dd
            },
            "Chunk": [
                {"uid":str, "text":str, "embed":list},
                {"uid":str, "text":str, "embed":list},
                ...
            ]
        }
        """
        #===========================================================================================================
        """
        ### Define relationships
        
        """
        for i,item in enumerate(data_json):
            print(i)
            # if i==14:
            #     print(item['Pic'])
            # create nodes
            document = Document.from_dict(item['Document'])
            self.create_node(document)
            
            highlights = []
            for ele in item['Highlight']:
                highlight = Highlight.from_dict(ele)
                highlights.append(highlight)
                self.create_node(highlight)
                
            time = Time.from_dict(item['Time'])
            self.create_node(time)
            
            chunks = []
            for ele in item['Chunk']:
                chunk = Chunk.from_dict(ele)
                chunks.append(chunk)
                self.create_node(chunk)
                
            role = Role.from_dict(item['Role'])
            if self.existed_node(role)==None:
                self.create_node(role)
            # else:
            #     pic = Pic.from_dict(existed_node(ele))
            #     pics.append(pic)
                
            
                
            # roles = []
            # for ele in item['Role']:
            #     if existed_node(ele)==None:
            #         role = Role.from_dict(ele)
            #         roles.append(role)
            #         self.create_node(role)
            #     else:
            #         role = Role.from_dict(existed_node(ele))
            #         roles.append(role)
                
            pics = []
            for ele in item['Pic']:
                pic = Pic.from_dict(ele)
                if self.existed_node(pic)==None:
                    pics.append(pic)
                    self.create_node(pic)
                else:
                    pics.append(pic)
            
            #==================================================
            #create relationships
            self.create_relationship(document, highlights, "HAS_HIGHLIGHT")
            self.create_relationship(document, chunks, "HAS_CHUNK")
            self.create_relationship(document, [time], "HAS_TIME")
            self.create_relationship(document, [role], "HAS_ROLE")
            self.create_relationship(document, pics, "HAS_PIC")
            
        print("Build KG successfully!")
            
    
    
    
    