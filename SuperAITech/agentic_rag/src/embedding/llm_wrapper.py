import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer, TextIteratorStreamer, StoppingCriteriaList
from threading import Thread
from transformers import StoppingCriteria, StoppingCriteriaList

# class StopOnTokens(StoppingCriteria):
#     def __init__(self, stop_ids):
#         self.stop_ids = stop_ids

#     def __call__(self, input_ids, scores, **kwargs):
#         # Stop if the last token in the sequence is in stop_ids
#         return input_ids[0, -1].item() in self.stop_ids


class LlmWrapper:
    def __init__(self, llm_name):
        self.__model = AutoModelForCausalLM.from_pretrained(
            llm_name,
            torch_dtype = torch.bfloat16,
            device_map= 'auto',
            # use_cache = True
        )
        self.__tokenizer = AutoTokenizer.from_pretrained(llm_name)
        self.__streamer = TextIteratorStreamer(self.__tokenizer, skip_prompt=True, skip_special_tokens=True)

    # def threaded_generation(self, conversations, **kwargs):
    #     text = self.__tokenizer.apply_chat_template(
    #             conversations,
    #             tokenize = False,
    #             add_generation_prompt = True
    #     )
    #     input_ids = self.__tokenizer(text, return_tensors="pt").input_ids.to(self.__model.device)
    #     output = self.__model.generate(input_ids, **kwargs)
    #     response = self.__tokenizer.decode(output[0], skip_special_tokens=True)
    #     return response

    def chat_with_llm(self, conversations, streaming=True):
        try:
            text = self.__tokenizer.apply_chat_template(
                conversations,
                tokenize = False,
                add_generation_prompt = True
            )
            model_inputs = self.__tokenizer(text, return_tensors='pt').to(self.__model.device)
            stop_token_ids = [self.__tokenizer.eos_token_id]
            generation_kwargs = dict(
                **model_inputs,
                max_new_tokens=2048,
                # do_sample = True,
                # stopping_criteria = StoppingCriteriaList([StopOnTokens(stop_token_ids)]),
                # # do_sample=True,
                eos_token_id=self.__tokenizer.eos_token_id,
                pad_token_id=self.__tokenizer.pad_token_id or self.__tokenizer.eos_token_id,
                #do_sample=True,
                temperature=0.2,
                # # top_p=0.7,
                # top_k=30,
                streamer=self.__streamer
            )
            # thread = Thread(target=self.threaded_generation, args=(conversations), kwargs=generation_kwargs)
            thread = Thread(target=self.__model.generate, kwargs=generation_kwargs)
            thread.start()
            response = ''
            for token in self.__streamer:
                if token != None:
                    if streaming:
                        print(token, end='', flush=True)
                    response += token
            return response
        except Exception as e:
            print(f'===== LlmWrapper fail... {e} =====')
            return None