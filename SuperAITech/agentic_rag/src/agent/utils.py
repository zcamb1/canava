def similarity_context(data):
    # with open(data_json, "r", encoding = "utf-8") as fr:
    #     data = json.load(fr)
    context_blocks = []
    i = 0
    for doc in data.values():
        i+=1
        title_doc = doc.get("title", "Không có thông tin về tiêu đề của tài liệu này.").capitalize()
        path_doc = doc.get("path", "Không có thông tin về đường dẫn của tài liệu này.")
        pics_arr = []
        pics = doc.get("pics", [])
        if len(pics)>=1 and pics[0]["pic_props"]!=None:
            for num_pic, props in enumerate(pics, start=1):
                pic = props['pic_props']
                rel_pic = props['rel_props']
                full_name = pic.get('full_name')
                knox_id = pic.get('knox_id')
                location = pic.get('location', 'Không có thông tin về vị trí ngồi.')
                phone = pic.get('phone', 'Không có thông tin về số điện thoại.')
                d = rel_pic.get('desc', ['Không có thông tin.'])
                desc = ', '.join(d)
                p = f"""
    {num_pic}. {full_name}
    - knox id: {knox_id}
    - Ví trí ngồi: {location}
    - Số điện thoại: {phone}
    - Các ghi chú: {desc}
"""
                pics_arr.append(p)
                    
        else:
            pics_arr.append("Không có thông tin về người phụ trách quản lý tài liệu này.")
            
        roles = doc.get("roles", [])
        roles_arr = []
        if len(roles)>=1 and roles[0]["role_props"]!=None:
            for num_role, props in enumerate(roles, start=1):
                role = props['role_props']
                rel_role = props['rel_props']
                title = role.get('title')
                c = rel_role.get('conditions', [f'Áp dụng cho toàn bộ {title}'])
                conditions = ', '.join(c)
                r = f"""
    {num_role}. {title}
    - Các điều kiện: {conditions}
"""
                roles_arr.append(r)
                    
        else:
            roles_arr.append("Không có thông tin về người phụ trách quản lý tài liệu này.")

        pics_str = "".join(pics_arr).rstrip()
        roles_str = "".join(roles_arr).rstrip()
        sorted_chunks = dict(sorted(doc['chunks'].items()))
        chunks_arr = []
        for k,v in sorted_chunks.items():
            ch = f"""
    [Trích đoạn {k+1}]:
    {v}
"""
            chunks_arr.append(ch)
        chunks_str = "".join(chunks_arr).rstrip()

        block = f"""---
[Tài liệu {i}: {title_doc}]
- Tiêu đề tài liệu: {title_doc}
- Đường dẫn tham khảo: {path_doc}

- Người phụ trách: {pics_str}

- Phạm vi áp dụng: {roles_str}

- Các trích đoạn: {chunks_str}
---"""
        context_blocks.append(block)
    return "\n".join(context_blocks)

def irrelevant_context():
    ir = f"""**Tin nhắn không liên quan đến mục đích vận hành của hệ thống**

Người dùng vừa đặt một câu hỏi hoặc tin nhắn không nằm trong phạm vi các tài liệu tham khảo hiện có.
Trong trường hợp này, yêu cầu bạn trả lời như sau:

1. Lịch sự vào chuyên nghiệp phản hồi một cách tích cực các tin nhắn xã giao, ví dụ như chào hỏi, cảm ơn hoặc từ chối khéo.
2. Không cố bịa đặt thông tin để phản hồi lại tin nhắn ngoài tài liệu tham khảo.
3. Hãy hướng người dùng đặt những câu hỏi liên quan đến nội dung các tài liệu dưới đây:
    - Chính sách liên quan đến Bảo hiểm                                                
    - Các bước làm phê duyệt Gen AI                                            
    - Các bước để yêu cầu cấp địa chỉ IP                                        
    - Các nội quy chung hiển nhiên đúng trong công ty                           
    - Các quy định bảo mật thông tin khi sử dụng RBS để làm việc tại nhà        
    - Chính sách nghỉ phát triển bản thân                                       
    - Danh sách nhân viên phụ trách PIC                                         
    - Giới thiệu về chatbot                                                     
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
    - Quy trình ứng phó với tai nạn và các tình huống nguy hiểm tại nơi làm việc
    - Quy trình sử dụng xe nội bộ 16 chỗ SRV
    - Quy trình xin cấp phát sửa chữa thiết bị IT
    - Quy định về an ninh mạng trong SRV
    - Sổ tay nhân viên 2025
    - Tổng quan về Samsung SRV
    - Tài liệu sơ cấp cứu
    - Thông tin về Các phần mềm bảo mật thông tin
    - Cập nhật Chính sách lao động khuyết tật
    - Các phần mềm độc hại thường gặp và cách ngăn chặn
    - Kiểm tra email trên điện thoại
    - Đặt một phòng họp trực tuyến
    
Hãy nhớ rằng, tuyệt đối KHÔNG được tự sáng tạo thông tin để phản hồi tin nhắn từ người dùng.
"""
    return ir

def graph_context(ans):
    g = """**Tin nhắn là câu hỏi phải truy vấn dữ liệu qua câu lệnh Cypher sử dụng trong Neo4j**
### Thông tin về schema lưu trữ trong Neo4j
#### Các Nodes:
- (Document {"uid", "label", "path", "title"})
- (Time {"uid", "label", "create_at", "efficient_time"})
- (Highlight {"uid", "label", "text", "embed"})
- (Chunk {"uid", "label", "text", "embed"})
- (Role {"uid", "label", "title"})
- (Pic { "uid", "label", "phone", "full_name", "knox_id", "location"})

#### Mô tả chi tiết các Nodes:
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

#### Các Relations:
- (Document)-[:HAS_TIME]->(Time)
- (Document)-[:HAS_HIGHLIGHT]->(Highlight)
- (Document)-[:HAS_CHUNK]->(Chunk)
- (Document)-[:HAS_ROLE {conditions}]->(Role)
- (Document)-[:HAS_PIC {desc}]->(Pic)

#### Mô tả chi tiết các Relationships:
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
    gg = f"""### Câu lệnh Cypher:
{ans['cypher']}

### Dữ liệu trả về:
{ans["result"]}

Bạn vừa nhận được thông tin về schema được lưu trữ trong cở sở dữ liệu đồ thị Neo4j và dữ liệu kết quả từ câu truy lệnh truy vấn Cypher.
Trong trường hợp này, yêu cầu bạn phải trả lời như sau:
- Dữ liệu này có thể là một số liệu, một danh sách node hoặc một vài thuộc tính.
- Không có thêm văn bản về nội dung văn bản đi kèm
- Khi trả lời bạn phải dựa trực tiếp vào schema và dữ liệu trả về được cung cấp bên trên, không được suy diễn gì thêm.
- Nếu dữ liệu chỉ đơn giản là con số hãy trả lời rõ ràng mạch lạc.
- Chỉ tập trung giải đáp câu hỏi, không phải giải thích gì thêm.
- Nếu không có kết quả nào, hãy từ chối trả lời.
"""
    ggg = g+gg

    return ggg