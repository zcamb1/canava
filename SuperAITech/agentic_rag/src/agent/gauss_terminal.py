import requests
import json
import time
import re
#from SuperAITech.agentic_rag.src.agent.similarity import Similarity
from similarity import Similarity
from utils import irrelevant_context, graph_context, similarity_context
from neo4j import GraphDatabase
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
result=''
def call_agent(url, api_key, payload):
  url = url
  
  headers = {
      "x-api-key": api_key,
      "Content-Type": "application/json"
  }
  payload = payload
  
  response = requests.post(url, headers=headers, json=payload)
  print(response.json())
  print(response.headers.get("Content-Type"))
  return response.json()['outputs'][-1]['outputs'][-1]['results']['message']['text']
  
def clean_resp(text):
  text = re.sub(r"<think>.*?</think>","",text, flags=re.DOTALL)
  #print(text)
  return text.strip()
  
def clean_resp2(text):
  text = text.split('</think>')[-1]
  #text = re.sub(r"<think>.*?</think>","",text, flags=re.DOTALL)
  #print(text)
  return text.strip()
  
def clean_cypher(text):
  match = re.search(r"```cypher\s*([\s\S]*?)\s*```",text, flags=re.IGNORECASE)
  if match:
    return match.group(1).strip()
  else:
    return text.strip()
  
def generate_cypher (question):
  url = 'https://agent.sec.samsung.net/api/v1/run/6139c523-5190-42bf-aca6-f4c58f602f46?stream=false'
  api_key = 'sk-NnCY6MlP7p0czCvg0uoPY-DYEdZa44YSjKoCXWI2ukM'
  payload = {
  "component_inputs": {
    "TextInput-zqTVD": {
      "input_value": question
    }}
  }
  resp = clean_resp(call_agent(url, api_key, payload))
  cypher = clean_cypher(resp)
  return cypher   
  
def run_query(driver, cypher):
  with driver.session() as session:
    try:
        res = session.run(cypher)
        return True, res.data()
    except Exception as e:
        return False, str(e)
def text2cypher(driver, question):
  cypher = generate_cypher(question)
  success, res = run_query(driver, cypher)
  print(f'GRAPH SEARCH: {res}\n')
  if success:
    return {"cypher":cypher, "result":res}
  else:
    return {"cypher":None, "error":f'Failed after 1 retries: {res}'}
  
  
def router(driver, similarity_search, question, session_id, conversation):
  global result
  url = 'https://agent.sec.samsung.net/api/v1/run/9c659431-296b-4a46-86d6-8b3a4c7a21dd?stream=false'
  api_key = 'sk-NnCY6MlP7p0czCvg0uoPY-DYEdZa44YSjKoCXWI2ukM'
  payload = {
    "component_inputs": {
      "ChatInput-vaPz7": {
        "input_value": question
      },
      "TextInput-Zp92A":{
        "input_value": session_id
      },
      "TextInput-D3Czf":{
        "input_value": conversation
      }
    }
  }
  call_agent(url, api_key, payload)
  resp = clean_resp2(result)
  resp = resp.replace("**"," ").strip()
  if len(resp)<20:
    if "TEXT_SEARCH" in resp:
      ans_dict = similarity_search.search(question)
      return {"GRAPH_QUERY":None, "TEXT_SEARCH":ans_dict, "IRRELEVANT":None, "CHIT_CHAT":None}
    elif "GRAPH_QUERY" in resp:
      ans = text2cypher(driver, question)
      if ans['cypher']==None:
        ans_dict = similarity_search.search(question)
        return {"GRAPH_QUERY":None, "TEXT_SEARCH":ans_dict, "IRRELEVANT":None, "CHIT_CHAT":None}
      else:
        return {"GRAPH_QUERY":ans, "TEXT_SEARCH":None, "IRRELEVANT":None, "CHIT_CHAT":None}
    elif "CHIT_CHAT" in resp:
      return {"GRAPH_QUERY":None, "TEXT_SEARCH":None, "IRRELEVANT":None, "CHIT_CHAT":1}
    elif "IRRELEVANT"  in resp:
      return {"GRAPH_QUERY":None, "TEXT_SEARCH":None, "IRRELEVANT":1, "CHIT_CHAT":None}
    else:
      ans_dict = similarity_search.search(question)
      return {"GRAPH_QUERY":None, "TEXT_SEARCH":ans_dict, "IRRELEVANT":None, "CHIT_CHAT":None}
  else:
    ans_dict = similarity_search.search(resp)
    return {"GRAPH_QUERY":None, "TEXT_SEARCH":ans_dict, "IRRELEVANT":None, "CHIT_CHAT":None}

def create_context(resp):
  ans = ''
  if resp['TEXT_SEARCH']:
    ans = similarity_context(resp['TEXT_SEARCH'])
  elif resp['GRAPH_QUERY']:
    print(resp['GRAPH_QUERY'])
    ans = graph_context(resp['GRAPH_QUERY'])
  else:
    ans = irrelevant_context(resp['TEXT_SEARCH'])
  return ans
    
def init():
  embed_model_path = "/media/hdd1/users/minhhieuph/han/models/halong_embedding/"
  NEO4J_URI = "bolt://localhost:7687"
  NEO4J_USER = "neo4j"
  NEO4J_PASS = "ginta2001"
  embed_model = HuggingFaceEmbedding(embed_model_path)
  database_dir = '/media/hdd1/users/nguyenluu/chat/SuperAITech/agentic_rag/data/faiss'
  driver = GraphDatabase.driver(NEO4J_URI, auth = (NEO4J_USER, NEO4J_PASS))
  similarity_search = Similarity(driver, embed_model, database_dir)
  return embed_model, driver, similarity_search
  
def answering(embed_model, driver,similarity_search, ques, session_id, conversation):
  r = router(driver, similarity_search, ques, session_id, conversation)
  context = create_context(r)
  url = 'https://agent.sec.samsung.net/api/v1/run/6ed2a2dc-6b00-4caa-9345-dfa21dabda7f?stream=false'
  api_key = 'sk-NnCY6MlP7p0czCvg0uoPY-DYEdZa44YSjKoCXWI2ukM'
  payload = {
  "component_inputs": {
    "TextInput-3QsJw": {
        "input_value": context
      },
    "TextInput-gfQxK": {
        "input_value": session_id
      },
    "ChatInput-8PeDy": {
        "input_value": ques
      }}
  }
  resp = call_agent(url, api_key, payload)
  return resp
  
if __name__=='__main__':
  embed_model, driver, similarity_search = init()
  ques = "knox id linh.tam phu? tra´ch bao nhiêu ta`i liê?u?"
  res = answering(embed_model, driver,similarity_search, ques, '1', '')
  print("================================================================")
  print(res)
  