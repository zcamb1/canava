import ollama
class LLMsGen:
    def __init__(self, model_name):
        self.__model = model_name
        r = self.chat([{"role":"system","content":"Bạn là một chat bot hỗ trợ bằng Tiếng Việt, hãy đưa ra các câu trả lời bằng Tiếng Việt nhé."},
                  {"role":"user","content":"Bạn đã sẵn sàng chưa, bắt đầu nhé."}])
        print(r)
        
        
    def chat(self, messages,temperature=0.7):
        options = {
            "temperature":temperature,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1
        }
        #==========================
        resp = ollama.chat(
            model=self.__model,
            messages = messages,
            options=options
        )
        return resp["message"]["content"]