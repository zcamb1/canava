from tqdm import tqdm
from llama_index.core.node_parser.text.sentence import SentenceSplitter

class TextSplitter:
    def __init__(self, embed_model):
        self.__embed_model = embed_model

    def chunk_documents(self, content, uid):
        try:
            chunks = []
            text_splitter = SentenceSplitter(
                chunk_size = 512, 
                chunk_overlap = 50, 
                separator = '.', 
                paragraph_separator='\n\n'
            )
            text_chunks = text_splitter.split_text(content)
            for idx, chunk in enumerate(text_chunks):
                tmp = {
                    'uid': f'{uid}_chunk_{idx}',
                    'text': chunk,
                    'embed': self.__embed_model.get_text_embedding(chunk)
                }
                chunks.append(tmp)
            return chunks
        except Exception as e:
            print("=====================================================================")
            print(f'[FAILED] src/processing/text_splitter.py \n[DETAIL] {e} \n')
            return None
