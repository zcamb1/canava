from neo4j import GraphDatabase
class Similarity:
    def __init__(self, driver):
        self.__driver = driver
        self.__driver.execute_query("""CREATE VECTOR INDEX all_chunks IF NOT EXISTS
                                    FOR (c:Chunk) ON c.embed
                                    OPTIONS {indexConfig:{
                                        `vector.dimensions`: 768,
                                        `vector.similarity_function`: 'cosine'
                                        }}""")
        
        
    def search_document(self, uid):
        query = """
                MATCH (n:Document {uid:$uid}) 
                RETURN n.title AS title, n.path AS path
                """
        with self.__driver.session() as session:
            res = session.run(query, uid=uid)
            res = res.single()
            if res:
                return res['title'], res['path']
        return None, None
    
    def search_pic_from_doc(self, uid):
        query = """
                MATCH (n:Document {uid:$uid}) 
                OPTIONAL MATCH (n)-[r:HAS_PIC]->(p:Pic)
                RETURN collect({full_name:p.full_name, knox_id:p.knox_id, relationship:r.desc}) AS pics
                """
        with self.__driver.session() as session:
            res = session.run(query, uid=uid)
            res = res.single()
            if res:
                return res['pics']
        return None
    
    def search(self,embed_ques, k, domain='All'):
        #self.create_index_vector()
        docs = {}
        if domain=='All':
            query = '''CALL db.index.vector.queryNodes('all_chunks', $k, $embed_ques)
                    YIELD node AS hits, score
                    RETURN hits.text AS text, hits.uid AS uid, score
                    ORDER BY score DESC
                    '''
            similar_records, _, _ = self.__driver.execute_query(query,k=k, embed_ques=embed_ques)
            
            for record in similar_records:
                uid_arr = record['uid'].split("_")
                doc_uid = f'{uid_arr[0]}_{uid_arr[1]}'
                title_doc, path_doc = self.search_document(doc_uid)
                if title_doc==None or path_doc==None:
                    continue
                pics = self.search_pic_from_doc(doc_uid)
                if doc_uid not in docs.keys():
                    docs[doc_uid] = {'title':title_doc, 'path':path_doc, 'pics':pics,'chunks':{}}
                chunk_uid = int(uid_arr[3])
                if chunk_uid not in docs[doc_uid]['chunks'].keys():
                    docs[doc_uid]['chunks'][chunk_uid]=record['text']
                
        return docs
    