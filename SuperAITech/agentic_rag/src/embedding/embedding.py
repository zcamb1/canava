# from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# class Embedding:
#     def __init__(self,model_path):
#         self.__model = HuggingFaceEmbedding(model_path)

#     def embed(self, text):
#         try:
#             # model = SentenceTransformer(self.__model_path)
#             text_embeddings = self.__model.get_text_embedding(text).tolist()
#             return text_embeddings
#         except Exception as e:
#             print("=====================================================================")
#             print(f'[FAILED] src/embedding/embedding.py \n[DETAIL] {e} \n')
#             return None