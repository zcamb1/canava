from neo4j import GraphDatabase
import faiss
import json
from llama_index.core import (
    SimpleDirectoryReader,
    load_index_from_storage,
    VectorStoreIndex,
    StorageContext,
)
from llama_index.vector_stores.faiss import FaissVectorStore
class Similarity:
    def __init__(self,driver, embed_model, db_dir, k=20):
        vector_store = FaissVectorStore.from_persist_dir(db_dir)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, persist_dir=db_dir
        )
        index = load_index_from_storage(storage_context=storage_context, embed_model = embed_model)
        self.retriever = index.as_retriever(similarity_top_k = k)
        self.driver = driver
    
    def search_from_doc(self, uid):
        query = """
                MATCH (d:Document {uid:$uid}) 
                OPTIONAL MATCH (d)-[r:HAS_PIC]->(p:Pic)
                OPTIONAL MATCH (d)-[y:HAS_ROLE]->(z:Role)
                WITH d, collect({
                    pic_props: properties(p),
                    rel_props: properties(r)
                }) AS pics,
                collect({
                    role_props: properties(z),
                    rel_props: properties(y)
                }) AS roles
                RETURN apoc.convert.toJson({
                    title: d.title,
                    path: d.path,
                    pics: pics,
                    roles: roles
                }) AS result
                """
        with self.driver.session() as session:
            check = session.run(query, uid=uid)
            res = check.single()
            data = None
            if res:
                data = json.loads(res["result"])
            return data
    
    def search(self,ques):
        nodes = self.retriever.retrieve(ques)
        docs = {}  
        for n in nodes:
            uid_arr = n.metadata['uid'].split("_")
            doc_uid = f'{uid_arr[0]}_{uid_arr[1]}'
            res = self.search_from_doc(doc_uid)
            if doc_uid not in docs.keys():
                docs[doc_uid] = {'title':res["title"], 'path':res["path"], 'pics':res["pics"],'roles':res["roles"],'chunks':{}}
            chunk_uid = int(uid_arr[3])
            if chunk_uid not in docs[doc_uid]['chunks'].keys():
                docs[doc_uid]['chunks'][chunk_uid]=n.text
                
        return docs
      