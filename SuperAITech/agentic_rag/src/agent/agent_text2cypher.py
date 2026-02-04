from neo4j import GraphDatabase
from tqdm import tqdm
import re
class Text2Cypher:
    def __init__(self,NEO4J_URI, NEO4J_USER, NEO4J_PASS, llm_model, schema = '', prompt = ''):
        self.__driver = GraphDatabase.driver(NEO4J_URI, auth = (NEO4J_USER, NEO4J_PASS))
        self.__model = llm_model
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
        self.__system_prompt = """
        Bạn là một công cụ chuyển đổi câu hỏi tự nhiên sang câu lệnh truy vấn Cypher trong Neo4j.
Hiện tại phiên bản Neo4j đang sử dụng là 2025.07.1, hãy đưa câu lệnh truy vấn phù hợp nhất với câu hỏi cho trước.
        """
        self.__user_prompt = """
        Bạn là một công cụ chuyển đổi câu hỏi tự nhiên sang câu lệnh Cypher trong Neo4j.
Hiện tại phiên bản Neo4j đang sử dụng là 2025.07.1, hãy đưa câu lệnh Cypher phù hợp nhất với câu hỏi cho trước.
Chú ý các yêu cầu dưới đây:
- Chỉ sử dụng các thông tin từ schema đã cung cấp để sinh ra cau lệnh Cypher phù hợp.
- Không được đưa ra câu lệnh có thông tin labels hoặc prooerties khác với schema đã cung cấp.
- Chỉ đưa ra duy nhất câu lệnh Cypher và không phải giải thích, không thêm bất kì mô tả nào thêm.

Hãy đưa ra câu lệnh truy vấn phù hợp nhất với câu hỏi dựa trên thông tin schema đã được cung cấp:
###Schema:
{schema}

###Câu hỏi:
{question}

###Câu lệnh truy vấn Cypher:
        """
        self.__error_prompt = """
        Bạn là một công cụ chuyển đổi câu hỏi tự nhiên sang câu lệnh truy vấn Cypher trong Neo4j.
Hiện tại phiên bản Neo4j đang sử dụng là 2025.07.1, hãy cung cấp lại câu lệnh Cypher khác phù hợp hơn với câu hỏi cho trước.
Chú ý các yêu cầu dưới đây:
- Chỉ sử dụng các thông tin từ schema đã cung cấp để sinh ra câu lệnh Cypher phù hợp.
- Không được đưa ra câu lệnh có thông tin label hoặc prooerties khác với shema đã cung cấp.
- Chỉ đưa ra duy nhất câu lệnh Cypher và không phải giải thích, không thêm bất kì mô tả nào thêm.

Tuy nhiên trong quá trình chuyển đổi trước đó, câu lệnh của bạn cung cấp đã gặp lỗi nên không thể áp dụng được. Hãy sinh lại câu lệnh Cypher CHÍNH XÁC với câu hỏi dựa trên thông tin schema đã được cung cấp, chỉ code và không phải giải thích gì thêm.
###Schema:
{schema}

###Câu hỏi:
{question}

###Lỗi trước đó:
{error}

###Câu lệnh Cypher khác:
        """
        
    def _clean_resp(self, text):
        text = re.sub(r'<think>.*?</think>',"",text, flags=re.DOTALL)
        return text.strip()
    
    def _generate_cypher (self, conversations, error_msg = None):
        messages = [
            {"role":"system", "content":self.__system_prompt},
        ]+conversations
        
        resp = self.__model.chat(messages)
        resp = self._clean_resp(resp)
        return resp
    
    def _run_query(self, cypher):
        with self.__driver.session() as session:
            try:
                res = session.run(cypher)
                return True, res.data()
            except Exception as e:
                return False, str(e)
            
    def query(self, question, max_retry = 3):
        error_msg = None
        prompt = self.__user_prompt.format(schema=self.__schema, question = question)
        conversations = [{"role":"user", "content":prompt}]
        for attempt in range(max_retry):
            cypher = self._generate_cypher(conversations, error_msg)
            print(cypher)
            success, res = self._run_query(cypher)
            if success:
                return {"cypher":cypher, "result":res}
            else:
                error_msg = res
                conversations.append({"role":"assistant", "content":cypher})
                error_prompt = self.__error_prompt.format(schema='', question='', error=error_msg)
                conversations.append({"role":"user", "content":error_prompt})
        return {"cypher":None, "error":f'Failed after {max_retry} retries: {error_msg}'}
    
    def close(self):
        self.__driver.close()