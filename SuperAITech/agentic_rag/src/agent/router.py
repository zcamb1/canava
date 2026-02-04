from src.agent.agent_text2cypher import Text2Cypher
from src.agent.similarity_search import Similarity
import re
class Router:
    def __init__(self, NEO4J_URI, NEO4J_USER, NEO4J_PASS, model, embed_model):
        self.NEO4J_URI=NEO4J_URI
        self.NEO4J_USER=NEO4J_USER
        self.NEO4J_PASS=NEO4J_PASS
        self.__embed_model = embed_model
        self.__llm_model = model
        self.__system_prompt = """
        Bạn là một bộ phân loại câu hỏi cho một hệ thống truy vấn.
Nhiệm vụ của bạn là phân loại câu hỏi từ người dùng vào **một trong hai loại dưới đây** dựa theo mô tả của chúng.
        """
        self.__user_prompt = """
        Bạn là một bộ phân loại câu hỏi cho một hệ thống truy vấn.
Nhiệm vụ của bạn là phân loại câu hỏi từ người dùng vào **một trong hai loại dưới đây** dựa theo mô tả của chúng.
Chú ý các yêu cầu sau đây:
- Bám sát vào những thông tin của từng loại để đưa ra lựa chọn tối ưu nhất
- Không phải giải thích gì thêm, chỉ trả về đúng một trong hai từ sau đó là "GRAPH_QUERY" hoặc "TEXT_SEARCH"

Hãy suy nghĩ thật kĩ và đưa ra lựa chọn tối ưu nhất có thể dựa trên thông tin của mỗi loại.
###Mô tả chi tiết
1. GRAPH_QUERY
- Schema được lưu trữ trong Neo4j như sau:
	{schema}
- Câu hỏi cần thông tin từ các dữ liệu đòi hỏi sự liên kết thông tin lưu trữ trong Neo4j
- Câu hỏi có thể có các định dạng liên quan tới việc đếm số lượng, liệt kê chi tiết, tìm kiếm cụ thể theo đối tượng,...
- Ví dụ:
	- knox_id linh.tam đảm nhiệm phụ trách bao nhiêu tài liệu? (Giải thích: Câu hỏi này đòi hỏi bạn phải đếm số kết nối từ Node Pic cói knox_id là linh.tam để đưa ra câu trả lời)
	- Tổng cộng có bao nhiêu tài liệu tham khảo được lưu trữ trong cơ sở dữ liệu? (Giải thích: Câu hỏi này đòi hỏi bạn phải đếm tổng cộng số Node Document để đưa ra được câu trả lời.)
2. TEXT_SEARCH
- Nội dung chi tiết về các loại tài liệu sẽ bao gồm:
	- Bảo hiểm                                                             
	- Các bước làm phê duyệt Gen AI
	- Các bước để yêu cầu cấp địa chỉ IP                                 
	- Các quy định bảo mật thông tin khi sử dụng RBS để làm việc tại nhà
	- Danh sách nhân viên phụ trách PIC
	- Giấy phép phần mềm                        
	- Hướng dẫn dùng Antivirus-V3                          
	- Hướng dẫn giải trình do cài đặt phần mềm vi phạm           
	- Hướng dẫn join domain Activate Directory                  
	- Hướng dẫn làm giải trình cho trường hợp bị block IP do cài đặt chơi game
	- Hướng dẫn thủ tục nhận trợ cấp gửi trẻ                     
	- Làm phê duyệt IT helpdesk                            
	- Phụ cấp ngoại ngữ
	- Phúc lợi Hiếu Hỷ                                
	- Phúc lợi thai sản
	- Phòng cháy chữa cháy
	- Quy trình sử dụng xe nội bộ 16 chỗ SRV
	- Quy trình xin cấp phát sửa chữa thiết bị IT
	- Quy định về an ninh mạng trong SRV
	- SỔ TAY NHÂN VIÊN BẢN SỬA ĐỔI NĂM 2025
	- Tài liệu sơ cấp cứu
	- Thông tin về Các phần mềm bảo mật thông tin
	- các phần mềm độc hại thường gặp và cách ngăn chặn
	- Kiểm tra email trên điện thoại
	- Đặt một phòng họp trực tuyến
- Câu hỏi liên quan đến các thông tin chi tiết có thể của một tài liệu cụ thể nào đó tồn tại trong Cơ sở dữ liệu.
- Câu hỏi có thể liên quan đến nội dung quy định, nội quy, chính sách, các phúc lợi hay thông tin chung liên quan đến công ty.
- Câu hỏi mà đòi hỏi phải lấy được nội dung trong một dữ liệu nào đó thì mới có thể trả lời được.
- Ví dụ:
	- Hãy cho tôi biết về các phúc lợi khi có ngoại ngữ trong SRV? (Câu hỏi này bạn phải trích xuất được nội dung về phúc lợi liên quan đến ngoại ngữ của công ty để đưa ra trả lời.)
	- Tôi có thể đặt xe công ty cho đám cưới của mình được không? (Câu hỏi này đòi hỏi bạn phải tìm kiếm toàn bộ thông tin liên quan đến các phúc lợi Hiếu Hỷ trong đó có mục cho thuê xe của công ty để đưa ra câu trả lời.)
	
Chỉ phản hồi đúng 1 trong 2 từ "GRAPH_QUERY" hoặc "TEXT_SEARCH", không phải giải thích thêm gì cả.

###Câu hỏi
{question}

###Câu trả lời:
        """
        self.__schema = """
        ####Các Nodes:
- (Document {"uid", "label", "path", "title"})
- (Time {"uid", "label", "create_at", "efficient_time"})
- (Highlight {"uid", "label", "text", "embed"})
- (Chunk {"uid", "label", "text", "embed"})
- (Role {"uid", "label", "title"})
- (Pic { "uid", "label", "phone", "full_name", "knox_id", "location"})

####Mô tả chi tiết các Nodes:
Node: (Document {"uid", "label", "path", "title"})
- Đại diện cho các tài liệu bao gồm chính sách, quy định hoặc phúc lợi công ty được lưu trong cơ sở dữ liệu Neo4j.
- Các thuộc tính:
	- uid: thuộc tính thể hiện unique id của một tài liệu.
	- label: thuộc tính thể hiện label Node của một tài liệu, luôn luôn là Document vì đây là Node Document.
	- path: thuộc tính thể hiện đường dẫn tham khảo của tài liệu.
	- title: thuộc tính thể hiện tên của tài liệu.

Node: (Time {"uid", "label", "create_at", "efficient_time"})
- Đại diện cho thời gian công bố và thời gian áp dụng của một tài liệu.
- Các thuộc tính:
	- uid: thuộc tính thể hiện unique id của thời gian.
	- label: thuộc tính thể hiện label Node của thời gian, luôn luôn là Time vì đây là Node Time.
	- create_at: thuộc tính thể hiện thời gian công bố tài liệu.
	- efficient_time: thuộc tính thể hiện thời gian tài liệu được áp dụng.
	
Node: (Highlight {"uid", "label", "text", "embed"})
- Đại diện cho các nội dung chính hoặc nội dung nổi bật của một tài liệu.
- Các thuộc tính:
	- uid: thuộc tính thể hiện unique id của Node Highlight.
	- label: thuộc tính thể hiện label của node Highlight, luôn luôn là Highlight vì đây là Node Highlight.
	- text: thuộc tính thể hiện cho mỗi nội dung chính hoặc nội dung nổi bật của tài liệu đó.
	- embed: thuộc tính thể hiện vector embedding của thuộc tính text trên nhằm phục vụ cho các truy vấn.
	
Node: (Chunk {"uid", "label", "text", "embed"})
- Đại diện cho các chunking của một tài liệu.
- Các thuộc tính:
	- uid: thuộc tính thể hiện unique id của Node Chunk.
	- label: thuộc tính thể hiện label của node Chunk, luôn luôn là Chunk vì đây là Node Chunk.
	- text: thuộc tính thể hiện nội dung chunk của tài liệu đó.
	- embed: thuộc tính thể hiện vector embedding của thuộc tính text trên nhằm phục vụ cho các truy vấn.

Node: (Role {"uid", "label", "title"})
- Đại diện cho các đối tượng được hưởng hoặc phải tuân theo một tài liệu.
- Các thuộc tính:
	- uid: thuộc tính thể hiện unique id của Node Role, luôn luôn là một trong các mã bao gồm {{"NVCT", "TTS", "PL", "GL"}}
	- label: thuộc tính thể hiện label của node Role, luôn luôn là Role vì đây là Node Role
	- title: thuộc tính thể hiện tên cụ thể của mỗi vai trò được hưởng hoặc phải tuân theo từ một tài liệu, luôn luôn là một trong các nội dung sau {{"Nhân viên chính thức", "Thực tập sinh", "Part Leader", "Group Leader"}}
	
Node: (Pic { "uid", "label", "phone", "full_name", "knox_id", "location"})
- Đại diện cho người phụ trách của một tài liệu
- Các thuộc tính:
	- uid: thuộc tính thể hiện unique id của Node Pic, thực ra uid của Node Pic giống hệt thuộc tính knox_id của nó.
	- label: thuộc tính thể hiện label của node Pic, luôn luôn là Role vì đây là Node Pic.
	- phone: thuộc tính thể hiện số điện thoại của người phụ trách tài liệu.
	- full_name: thuộc tính thể hiện đầy đủ họ tên của người phụ trách tài liệu.
	- knox_id: thuộc tính thể hiện knox id của người phụ trách tài liệu.
	- location: thuộc tính thể hiện vị trí ngồi trong công ty của người phụ trách tài liệu.

####Các Relations:
- (Document)-[:HAS_TIME]->(Time)
- (Document)-[:HAS_HIGHLIGHT]->(Highlight)
- (Document)-[:HAS_CHUNK]->(Chunk)
- (Document)-[:HAS_ROLE {conditions}]->(Role)
- (Document)-[:HAS_PIC {desc}]->(Pic)

####Mô tả chi tiết các Relationships:
Relationship: (Document)-[:HAS_TIME]->(Time)
- Ý nghĩa: Mỗi một Document sẽ có quan hệ HAS_TIME với Time

Relationship: (Document)-[:HAS_HIGHLIGHT]->(Highlight)
- Ý nghĩa: Mỗi một Document sẽ có quan hệ HAS_HIGHLIGHT với Highlight

Relationship: (Document)-[:HAS_CHUNK]->(Chunk)
- Ý nghĩa: Mỗi một Document sẽ có quan hệ HAS_CHUNK với Chunk

Relationship: (Document)-[:HAS_ROLE {conditions}]->(Role)
- Ý nghĩa: Mỗi một Document sẽ có quan hệ HAS_ROLE với Role
- Các thuộc tính:
	- conditions: thuộc tính này thể hiện rằng đối với mỗi quy định, người thụ hưởng có thể có hoặc không phải tuân theo các điều kiện được hiển thị trong thuộc tính conditions này

Relationship: (Document)-[:HAS_PIC {desc}]->(Pic)
- Ý nghĩa: Mỗi một Document sẽ có quan hệ HAS_PIC với Pic
- Các thuộc tính:
	- desc: thuộc tính này thể hiện rằng đối với mỗi một người phụ trách có thể có hoặc không các mô tả chi tiết riêng đối với từng tài liệu riêng lẻ
        """
        self.__module_desc = """"""

    def _clean_resp(self, text):
        text = re.sub(r'<think>.*?</think>',"",text, flags=re.DOTALL)
        return text.strip()
        
    def assign(self, question, max_loop = 2):
        prompt = self.__user_prompt.format(schema=self.__schema, question = question)
        messages = [{"role":"system", "content":self.__system_prompt},
                   {"role":"user", "content":prompt}]
        for i in range(max_loop):
            resp = self.__llm_model.chat(messages)
            resp = self._clean_resp(resp)
            if resp=="GRAPH_QUERY":
                text2cypher = Text2Cypher(self.NEO4J_URI, self.NEO4J_USER, self.NEO4J_PASS, self.__llm_model)
                ans = text2cypher.query(question)
                return {"GRAPH_QUERY":ans, "TEXT_SEARCH":None}
            elif resp=="TEXT_SEARCH":
                similarity = Similarity(self.NEO4J_URI, self.NEO4J_USER, self.NEO4J_PASS)
                embed_ques = self.__embed_model.get_text_embedding(question)
                ans_dict = similarity.search(embed_ques,20)
                return {"GRAPH_QUERY":None, "TEXT_SEARCH":ans_dict}
            elif i==max_loop-1:
                similarity = Similarity(self.NEO4J_URI, self.NEO4J_USER, self.NEO4J_PASS)
                embed_ques = self.__embed_model.get_text_embedding(question)
                ans_dict = similarity.search(embed_ques,20)
                return {"GRAPH_QUERY":None, "TEXT_SEARCH":ans_dict}
            else:
                messages.append({"role":"assistant", "content":resp})
                messages.append({"role":"user", "content":prompt})
            
        
        