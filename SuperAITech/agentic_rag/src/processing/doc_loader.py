import os
from tqdm import tqdm
import json
import unicodedata
class DocumentLoader:
    def __init__(self, data_path, embed_model, text_splitter):
        self.__data_path = data_path
        self.__embed_model=embed_model
        self.__text_splitter=text_splitter

    def load_documents(self):
        # try:
            roleee={
                unicodedata.normalize('NFC','nhân viên chính thức'): 'NVCT',
                unicodedata.normalize('NFC','thực tập sinh'): 'TTS',
                unicodedata.normalize('NFC','part leader'): 'PL',
                unicodedata.normalize('NFC','group leader'): 'GL'
                
            }
            # print(roleee)
            res = []
            with open(self.__data_path, 'r', encoding='utf-8') as fr:
                data = json.load(fr)
                fr.close()
            for i in tqdm(range(0,len(data),1), desc = "Downloading data..."):
                tmp = data[i].copy()
                uid = f'doc_{i}'
                tmp['Document']['uid']=uid
                tmp['Role']['uid']=roleee[tmp['Role']['title'].lower()]
                tmp['Time']['uid']= f'{uid}_time'
                for pic_i, pic in enumerate(tmp['Pic']):
                    pic['uid'] = f'{pic['knox_id']}'
                highlights = tmp['Highlight']
                tmp['Highlight'] = []
                for hi, h in enumerate(highlights):
                    text_h = h
                    embed_h = self.__embed_model.get_text_embedding(h)
                    tmp_h = {'uid':f'{uid}_highlight_{hi}','text':text_h, 'embed':embed_h}
                    tmp['Highlight'].append(tmp_h)
                with open(tmp['Path'], 'r', encoding='utf-8') as fr:
                    lines = fr.readlines()
                    fr.close()
                full_text = ' '.join(lines)
                arr = self.__text_splitter.chunk_documents(full_text, uid)
                del tmp['Path']
                tmp['Chunk']=arr
                res.append(tmp)
            print(f'Download data successfully: {len(res)} contexts in dataset...')
            return res
        # except Exception as e:
        #     print("=====================================================================")
        #     print(f'[FAILED] src/processing/doc_loader.py \n[DETAIL] {e} \n')
        #     return None