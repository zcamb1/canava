from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from processing.doc_loader import DocumentLoader
from processing.doc_loader import TextSplitter
if __name__ == '__main__':
    embed_model_path = ''
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASS = "ginta2001"
    data_path = '/asr-shared/vi-VN/data/quocanh/HT/wav2vec2/Bot/SimpleRAG/data_new/abc.json'
    
    # driver = GraphDatabase.driver(NEO4J_URI, auth = (NEO4J_USER, NEO4J_PASS))
    embed_model = HuggingFaceEmbedding(embed_model_path)
    text_splitter = TextSplitter(embed_model)
    documentLoader = DocumentLoader(data_path, embed_model, text_splitter)
    data = documentLoader.load_documents()
    kg_builder = KGBuilder(NEO4J_URI, NEO4J_USER, NEO4J_PASS)
    kg_builder.build_graph_base(data)
    
    
    