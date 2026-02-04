import json
import re
class AnswerCritic:
    def __init__(self,model):
        self.__system_prompt = """
        Bạn là một chuyên gia trong việc xác định xem câu hỏi đã được trả lời đầy đủ và chính xác nhất hay chưa hoặc có cơ hội để bổ sung thêm thông tin cho câu trả lời hay không.
Người dùng sẽ cung cấp cho bạn một *câu hỏi* cùng các *tài liệu tham khảo* ứng với câu hỏi đó và cả *câu trả lời tương ứng với câu hỏi và tài liệu được cung cấp*. Nhiệm vụ của bạn đó là dựa vào các tiêu chí đánh giá dưới đây để xem rằng liệu câu hỏi đó đã được giải đáp đầy đủ, chính xác hay chưa. Nếu câu trả lời còn thiếu thông tin nào, bạn hãy đưa ra một bộ các câu hỏi mới để thu thập những thông tin còn thiếu đó.
        """
        self.__user_prompt = """
        Người dùng sẽ cung cấp cho bạn một *câu hỏi* cùng các *tài liệu tham khảo* ứng với câu hỏi đó và cả *câu trả lời tương ứng với câu hỏi và tài liệu được cung cấp*. Nhiệm vụ của bạn đó là dựa vào các tiêu chí đánh giá dưới đây để xem rằng liệu câu hỏi đó đã được giải đáp đầy đủ, chính xác hay chưa. Nếu câu trả lời còn thiếu thông tin nào, bạn hãy đưa ra một bộ các câu hỏi mới để thu thập những thông tin còn thiếu đó.
Chú ý các yêu cầu sau đây:
- Phải đánh giá chính xác câu trả lời dựa trên câu hỏi và tài liệu tham khảo được cung cấp dựa trên các tiêu chí dưới bên dưới.
- Không cần giải thích gì thêm, chỉ cần đưa ra câu trả lời theo đúng định dạng dưới json đây.

###Định dạng câu trả lời
- Nếu câu trả lời **đã đầy đủ và chính xác**, cung cấp output JSON:
{{
	"status": "accept"
}}

- Nếu câu trả lời **chưa đầy đủ**, cung cấp output JSON:
{{
	"status": "reject",
	"questions": ["câu hỏi bổ sung 1", "câu hỏi bổ sung 2, ..."]
}}

###Tiêu chí đánh giá:
####Tiêu chí về tính chính xác.
- Câu trả lời chính xác phải hoàn toàn dựa trên tài liệu tham khảo, tuyệt đối không thêm bớt thông tin khác từ bên ngoài.
- Một câu trả lời chính xác không được phép chắp nối thông tin linh tinh từ nhiều tài liệu tham khảo lại một cách vô nghĩa.
	- Ví dụ: Trong tài liệu tham khảo có 2 tài liệu nhưng một tài liệu có đường dẫn (gọi tắt là tài liệu A), một tài liệu không có đường dẫn (gọi tắt là tài liệu B). Trong khi đó câu trả lời lại lấy nội dung của tài liệu A (tài liệu không có đường dẫn) nối với đường dẫn trên tài liệu B (tài liệu có đường dẫn). Như vậy, trường hợp vừa nêu không phải là một cầu trả lời chính xác vì thông tin câu trả lời cung cấp sai hoàn toàn khi kết hợp giữa những tài liệu khác nhau.

####Tiêu chí về tính đầy đủ.
- Một câu trả lời đầy đủ phải giải đáp được tất cả các ý mà câu hỏi đặt ra.
- Câu trả lời đầy đủ nhất cần phải cung cấp **đường dẫn tài liệu tham khảo** và những **lưu ý quan trọng** nếu có.

Hãy đưa ra đánh giá chính xác nhất có thể từ câu hỏi, tài liệu tham khảo và nội dung câu trả lời cho trước dựa trên các tiêu chí đánh giá đã đặt ra. Chú ý trả lời đúng định dạng JSON đã quy định và không phải giải thích thêm gì.
###Câu hỏi:
{question}

###Tài liệu tham khảo:
{context}

###Câu trả lời cho trước:
{answer}

###Đánh giá của bạn:
        """
        self.__llm_model = model
    def _clean_resp(self, text):
        text = re.sub(r'<think>.*?</think>',"",text, flags=re.DOTALL)
        return text.strip()
    def critique_answers(self, question, context, answer, max_loop=3):
        for i in range(max_loop):
            prompt = self.__user_prompt.format(question=question, context=context, answer=answer)
            messages = [{"role":"system", "content":self.__system_prompt},
                       {"role":"user", "content":prompt}]
            resp = self._clean_resp(self.__llm_model.chat(messages))
            try:
                r = json.loads(resp)
                if 'status' in r.keys() and resp['status']=='accept':
                    return answer
                if 'status' in r.keys():
                    return f'REJECT:\n{answer}'
            except:
                print(resp)
                pass
        return f'FAILED PARSE:\n{answer}'
                
            
            