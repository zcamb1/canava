from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from src.agent.llm_gen import LLMsGen
from src.agent.router import Router
from src.agent.agent_answer_critic import AnswerCritic
def create_context(resp):
    ans  =[]
    if resp['GRAPH_QUERY'] and resp['GRAPH_QUERY']['cypher']:
        ans.append("Sử dụng truy vấn Cypher để tìm kiếm đáp án cho câu hỏi.\n")
        ans.append("###Cypher.\n")
        ans.append(resp['GRAPH_QUERY']['cypher']+'\n')
        ans.append("###Kết quả truy vấn:")
        ans.append(resp['GRAPH_QUERY']['result']+'\n')
    elif resp['GRAPH_QUERY'] and resp['GRAPH_QUERY']['cypher']==None:
        ans.append("Sử dụng truy vấn Cypher để tìm kiếm đáp án cho câu hỏi. Tuy nhiên kết quả truy vấn không phù hợp với câu hỏi đã cho\n")
    else:
        ans_dict = resp['TEXT_SEARCH']
        for doc in ans_dict.values():
            ans.append('===== START OF DOCUMENT =====\n')
            ans.append(f'**Tiêu đề tài liệu**: {doc['title']}\n')
            ans.append(f'**Đường dẫn tham khảo**: {doc['path']}\n\n')
            ans.append(f'**Các trích dẫn dưới đây là các ngữ cảnh của tài liệu được cung cấp**:\n')
            sorted_chunks = dict(sorted(doc['chunks'].items()))
            for chunk_key, chunk_value in sorted_chunks.items():
                ans.append(f'*Trích dẫn số {chunk_key}:*\n')
                ans.append(f'{chunk_value}\n\n')
                ans.append(f'Tài liệu tham khảo: {doc['title']}\n')
                ans.append(f'Đường dẫn tham khảo: {doc['path']}\n\n')
            if len(doc['pics'])>0:
                ans.append(f'**Danh sách người phục trách và các lưu ý quan trọng bao gồm:**\n')
                for pic in doc['pics']:
                    ans.append(f'- Người phục trách: {pic['full_name']} (knox id: {pic['knox_id']})\n')
                    # if len(pic['relationship'])>0:
                    #     print('Các lưu ý:\n')
                    #     for r in pic['relationship']:
                    #         ans.append(f'- {r}\n')
            ans.append('===== END OF DOCUMENT =====\n\n')
    with open('answers.txt','w', encoding='utf-8') as fw:
        fw.writelines(ans)
        fw.close()
    return ans
def context_log(question):
    embed_ques = embed_model.get_text_embedding(question)
    ans_dict = similarity.search(embed_ques,20)
    ans = []
    for doc in ans_dict.values():
        ans.append('===== START OF DOCUMENT =====\n')
        ans.append(f'**Tiêu đề tài liệu**: {doc['title']}\n')
        ans.append(f'**Đường dẫn tham khảo**: {doc['path']}\n\n')
        ans.append(f'**Các trích dẫn dưới đây là các ngữ cảnh của tài liệu được cung cấp**:\n')
        sorted_chunks = dict(sorted(doc['chunks'].items()))
        for chunk_key, chunk_value in sorted_chunks.items():
            ans.append(f'*Trích dẫn số {chunk_key}:*\n')
            ans.append(f'{chunk_value}\n\n')
            ans.append(f'Tài liệu tham khảo: {doc['title']}\n')
            ans.append(f'Đường dẫn tham khảo: {doc['path']}\n\n')
        if len(doc['pics'])>0:
            ans.append(f'**Danh sách người phục trách và các lưu ý quan trọng bao gồm:**\n')
            for pic in doc['pics']:
                ans.append(f'- Người phục trách: {pic['full_name']} (knox id: {pic['knox_id']})\n')
                # if len(pic['relationship'])>0:
                #     print('Các lưu ý:\n')
                #     for r in pic['relationship']:
                #         ans.append(f'- {r}\n')
        ans.append('===== END OF DOCUMENT =====\n\n')
    with open('answers.txt','w', encoding='utf-8') as fw:
        fw.writelines(ans)
        fw.close()
    return ans
def main(ques):
    embed_model_path = '/asr-shared/th-TH/users/hieupm/Code/nlp4s/ragvnlegaltext/models/embedding/halong_embedding'
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASS = "ginta2001"
    llm_name = 'qwen3:32b'
    embed_model = HuggingFaceEmbedding(embed_model_path)
    system_prompt = """Bây giờ bạn sẽ trở thành một trợ lý ảo Tiếng Việt tên Polaris. 
    Bạn là sản phẩm trí tuệ được tạo ra bởi 3 kĩ sư AI thuộc bộ phận Language AI tại công ty Samsung SRV.
    Bạn phải dựa vào các tài liệu chứa nhiều trích dẫn để đưa ra câu trả lời hữu ích nhất có thể.
    Nếu tồn tại tài liệu chứa thông tin giải đáp được câu hỏi, bạn bắt buộc phải trả lời đầy đủ các ý chính dưới đây:
    - Nội dung trả lời của bạn
    - Tên tài liệu bạn đã tham khảo
    - Đường dẫn của tài liệu mà bạn đã tham khảo
    """
    template = """
    **Chú ý các yêu cầu sau đây:**
    - Hãy trả lời rõ ràng, giải thích chi tiết nếu ngữ cảnh có câu trả lời
    - Luôn luôn cung cấp đường dẫn tham khảo từ tài liệu mà bạn lấy câu trả lời 
    - Hãy chọn lọc kĩ thông tin từng những tài liệu được cung cấp một cách phù hợp và chỉ được sử dụng thông tin có trong ngữ cảnh được cung cấp, **không được phép suy diễn gì thêm linh tinh**
    - Nếu tồn tại tài liệu chứa thông tin giải đáp được câu hỏi, bạn bắt buộc phải trả lời đầy đủ các nội dung bao gồm *Nội dung trả lời của bạn*, *Tên tài liệu bạn đã tham khảo*, *Đường dẫn của tài liệu mà bạn đã tham khảo*
    - Chỉ cần từ chối trả lời và không suy luận gì thêm nếu không có tài liệu nào cung cấp ngữ cảnh phù hợp
    
    ###Ví dụ:
    Câu hỏi:
    Cho tôi biết về phúc lợi Tiếng Anh có trong SRV/
    
    Câu trả lời không hợp lệ:
    Tại Samsung SRV, có chế độ phúc lợi phụ cấp cho những nhân viên có trình độ ngoại ngữ Tiếng Anh theo thông báo chính thức của tập đoàn. Cụ thể, thông báo chính thức áp dụng từ ngày 11 tháng 02 năm 2019 nhằm mục đích khích lệ nhân viên nâng cao khả năng giao tiếp tiếng Anh. Các đối tượng và chứng chỉ áp dụng trong chính sách phụ cấp ngoại ngữ tiếng Anh bao gồm toàn bộ nhân viên cung cấp các chứng chỉ chính thức như TOEIC Speaking, OPIC.
    Mức phụ cấp trong chính sách phụ cấp ngoại ngữ Tiếng Anh được chia làm 3 mức như sau:
    1. Đối với những nhân viên đạt trình độ ngoại ngữ tiếng Anh ở mức level 1 (phải có chứng chỉ OPIC trình độ Intermediate Mid hoặc TOEIC Speaking 130 điểm đến 150 điểm) sẽ được phụ cấp 3.000.000 VND một lần cho cấp độ này.
    2. Đối với các nhân viên đạt trình độ ngoại ngữ Tiếng Anh ở mức level 2 (phải cung cấp chứng chỉ OPIC ở mức Intermediate High hoặc TOEIC Speaking đạt từ 160 đến 180 điểm) sẽ được nhận phụ cấp 4.000.000 VNĐ một lần cho cấp độ này.
    3. Đối với các nhân viên đạt trình độ ngoại ngữ tiếng Anh ở level 3 (tức là có chứng chỉ OPIC Advance hoặc TOEIC Speaking từ 190 đến 200 điểm) sẽ nhận mức phụ cấp 6.000.000 một lần cho cấp độ này.
    Lưu ý rằng đối với chính sách phụ cấp Tiếng Anh sẽ ghi nhận trình độ của bạn và chi trả phụ cấp tương ứng với trình độ mà chứng chỉ bạn nộp.
    
    Câu trả lời hợp lệ phải có đầy đủ các nội dung bao gồm *Nội dung trả lời của bạn*, *Tên tài liệu bạn đã tham khảo*, *Đường dẫn của tài liệu mà bạn đã tham khảo*:
    Tại Samsung SRV, có chế độ phúc lợi phụ cấp cho những nhân viên có trình độ ngoại ngữ Tiếng Anh theo thông báo chính thức của tập đoàn. Cụ thể, thông báo chính thức áp dụng từ ngày 11 tháng 02 năm 2019 nhằm mục đích khích lệ nhân viên nâng cao khả năng giao tiếp tiếng Anh. Các đối tượng và chứng chỉ áp dụng trong chính sách phụ cấp ngoại ngữ tiếng Anh bao gồm toàn bộ nhân viên cung cấp các chứng chỉ chính thức như TOEIC Speaking, OPIC.
    Mức phụ cấp trong chính sách phụ cấp ngoại ngữ Tiếng Anh được chia làm 3 mức như sau:
    1. Đối với những nhân viên đạt trình độ ngoại ngữ tiếng Anh ở mức level 1 (phải có chứng chỉ OPIC trình độ Intermediate Mid hoặc TOEIC Speaking 130 điểm đến 150 điểm) sẽ được phụ cấp 3.000.000 VND một lần cho cấp độ này.
    2. Đối với các nhân viên đạt trình độ ngoại ngữ Tiếng Anh ở mức level 2 (phải cung cấp chứng chỉ OPIC ở mức Intermediate High hoặc TOEIC Speaking đạt từ 160 đến 180 điểm) sẽ được nhận phụ cấp 4.000.000 VNĐ một lần cho cấp độ này.
    3. Đối với các nhân viên đạt trình độ ngoại ngữ tiếng Anh ở level 3 (tức là có chứng chỉ OPIC Advance hoặc TOEIC Speaking từ 190 đến 200 điểm) sẽ nhận mức phụ cấp 6.000.000 một lần cho cấp độ này.
    Lưu ý rằng đối với chính sách phụ cấp Tiếng Anh sẽ ghi nhận trình độ của bạn và chi trả phụ cấp tương ứng với trình độ mà chứng chỉ bạn nộp.
    Tài liệu tham khảo: Chính sách phụ cấp ngoại ngữ
    Đường dẫn tham khảo: \\107.98.48.222\1. HR Guide\1. HR GUIDE\3. TOEIC-TOPIK(OPICs)

---
    Hãy trả lời câu hỏi dựa trên các ngữ cảnh sau:
    ### Ngữ cảnh:
    {context}

    ### Câu hỏi:
    {question}

    ### Trả lời:"""
    model = LLMsGen(llm_name)
    router = Router(NEO4J_URI, NEO4J_USER, NEO4J_PASS, model, embed_model)
    resp = router.assign(ques)
    context = ' '.join(create_context(resp))
    p = template.format(context = context, question=ques)
    messages = [{"role":"system","content":system_prompt},
               {"role":"user","content":p}]
    answer = model.chat(messages)
    critic = AnswerCritic(model)
    ans = critic.critique_answers(ques, context, answer)
    return ans
    