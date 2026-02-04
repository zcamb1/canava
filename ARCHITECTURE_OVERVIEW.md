# 🏗️ KIẾN TRÚC ĐƠN GIẢN HÓA - POLICYBOT

## 📌 Tóm tắt 1 câu:
> **React Frontend** gọi **FastAPI Backend**, Backend gọi **RAG Agent** để tìm kiếm + trả lời câu hỏi.

---

## 🎨 DIAGRAM ĐƠN GIẢN

```
┌─────────────────┐
│   TRÌNH DUYỆT   │  👤 User gõ câu hỏi
│   (React App)   │
└────────┬────────┘
         │ HTTP API
         ├──────────────────────────────────┐
         │                                  │
    [Gửi câu hỏi]                    [Nhận trả lời]
         │                                  │
         ▼                                  │
┌─────────────────┐                         │
│  FASTAPI SERVER │  🔌 10 endpoints        │
│    (main.py)    │     như /agent_chat     │
└────────┬────────┘                         │
         │                                  │
         ├──[Gọi Agent]──────────────┐      │
         │                           │      │
         ▼                           ▼      │
┌─────────────────┐          ┌─────────────────┐
│  SQLite DB      │          │  RAG AGENT      │
│                 │          │  (agent_gauss)  │
│ • conversations │          │                 │
│ • users         │          │ 1. Router       │──┐
│ • banned_users  │          │ 2. Search       │  │
└─────────────────┘          │ 3. LLM Answer   │  │
                             └────────┬────────┘  │
                                      │           │
                         ┌────────────┴────────┐  │
                         │                     │  │
                         ▼                     ▼  │
                  ┌─────────────┐      ┌─────────────┐
                  │   FAISS     │      │   Neo4j     │
                  │  (Vector    │      │  (Graph     │
                  │  Database)  │      │  Database)  │
                  └─────────────┘      └─────────────┘
                         │                     │
                         └──────────┬──────────┘
                                    │
                          [Tìm thấy context]
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Samsung LLM Agent  │
                         │  (External API)     │
                         └──────────┬──────────┘
                                    │
                             [Generate answer]
                                    │
                                    └─────────────────────┘
                                                          │
                                                          ▼
                                                   [Stream về user]
```

---

## 🔄 FLOW CHI TIẾT (5 BƯỚC)

### **BƯỚC 1: User nhập câu hỏi**
```
User gõ: "Knox ID là gì?"
         ↓
InputBar.jsx → handleSendMessage()
         ↓
Gọi: callFastAPIRagAPIFunc(userId, convId, "Knox ID là gì?")
```

### **BƯỚC 2: Frontend gọi Backend**
```
Frontend
    ↓ (HTTP GET)
http://107.98.158.222:9000/agent_chat?query=Knox%20ID%20l%C3%A0%20g%C3%AC?&userid=xxx&conid=yyy
    ↓
Backend (main.py) nhận request
```

### **BƯỚC 3: Backend gọi RAG Agent**
```python
# main.py - line 41-51
@app.get("/agent_chat")
async def chat(query, userid, conid):
    # Load conversation history
    conversation = await get_specific_conversation(userid, conid)
    
    # Format history
    conversation_history = format_messages(conversation.messages)
    
    # Call Agent
    return StreamingResponse(
        answering(embed_model, driver, similarity_search, 
                  query, conid, conversation_history)
    )
```

### **BƯỚC 4: Agent xử lý**
```python
# agent_gauss.py
def answering(embed_model, driver, similarity_search, question, session_id, conversation):
    # Step 1: Router - Phân loại câu hỏi
    route_result = router(driver, similarity_search, question, session_id, conversation)
    # Result: {"TEXT_SEARCH": {...}, "GRAPH_QUERY": None, ...}
    
    # Step 2: Tìm context từ database
    context = create_context(route_result)
    # Context: "Knox ID là hệ thống quản lý thiết bị..."
    
    # Step 3: Gọi LLM với context
    payload = {
        "context": context,
        "question": question
    }
    response = call_agent_stream(SAMSUNG_AGENT_URL, API_KEY, payload)
    
    # Step 4: Stream response về
    yield from response
```

### **BƯỚC 5: Frontend nhận và hiển thị**
```javascript
// messageAPI.js - callFastAPIRagAPI()
const reader = response.body.getReader();
while (true) {
    const {value, done} = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    onChunk(chunk); // Update UI real-time
}

// MessageContext.jsx
setMessages(prev => {
    const lastMessage = prev[prev.length - 1];
    return [...prev.slice(0, -1), {
        ...lastMessage,
        text: lastMessage.text + chunk  // Append chunk
    }];
});
```

---

## 🗂️ FILE QUAN TRỌNG (TOP 10)

### **Frontend:**
1. `src/components/chat/InputBar.jsx` - Ô nhập tin nhắn
2. `src/context/MessageContext.jsx` - Quản lý messages
3. `src/context/ConversationContext.jsx` - Quản lý conversations
4. `src/services/messageAPI.js` - API gọi chat

### **Backend:**
5. `main.py` - API server chính
6. `SuperAITech/agentic_rag/src/agent/agent_gauss.py` - Core RAG logic
7. `SuperAITech/agentic_rag/src/agent/similarity.py` - Vector search
8. `SuperAITech/agentic_rag/src/agent/utils.py` - Context formatting

### **Config:**
9. `src/config.js` - Backend URL
10. `package.json` - Dependencies frontend

---

## 🔑 CÁC KHÁI NIỆM QUAN TRỌNG

### **1. RAG (Retrieval-Augmented Generation)**
```
Câu hỏi → Tìm kiếm context → LLM + Context → Trả lời
```
**Ví dụ:**
- **Không có RAG**: LLM chỉ biết kiến thức có sẵn
- **Có RAG**: LLM + context từ database công ty = Trả lời chính xác về nội bộ

### **2. Vector Search (FAISS)**
```
Text → Embedding (số vector) → Lưu vào FAISS → Tìm kiếm tương tự
```
**Ví dụ:**
- "Knox ID" → [0.2, 0.8, 0.1, ...]
- Tìm vectors gần nhất → Tìm documents liên quan

### **3. Knowledge Graph (Neo4j)**
```
Entities → Relationships → Graph → Query bằng Cypher
```
**Ví dụ:**
```
(User)-[:HAS_ACCESS_TO]->(Document)
(Document)-[:BELONGS_TO]->(Department)
```

### **4. Streaming Response**
```
Không phải: [Đợi 10s] → Hiện toàn bộ câu trả lời
Mà là:     [0.1s] → "K"
           [0.1s] → "no"
           [0.1s] → "x "
           [0.1s] → "ID"
           ...
```

### **5. Context API (React)**
```
Thay vì:
  Component A → props → Component B → props → Component C

Dùng Context:
  Component A ──┐
  Component B ──┼──> Context Store <── Read/Write
  Component C ──┘
```

---

## 🛠️ TECH STACK SUMMARY

| Layer | Tech | Mục đích |
|-------|------|---------|
| **Frontend** | React 19 | UI framework |
| | Vite | Build tool (nhanh hơn Webpack) |
| | Tailwind CSS | Styling |
| | Context API | State management |
| **Backend** | FastAPI | API framework (Python) |
| | SQLite | Database nhỏ gọn |
| | Uvicorn | ASGI server |
| **AI/RAG** | LangChain | RAG framework |
| | FAISS | Vector database |
| | Neo4j | Graph database |
| | HuggingFace | Embedding model |
| | Samsung Agent | LLM (External API) |

---

## 📊 DATA FLOW CHART

```
┌───────────────────────────────────────────────────────────┐
│  USER INPUT: "Knox ID là gì?"                             │
└───────────────┬───────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────┐
│  FRONTEND (React)                                          │
│  1. User types in InputBar                                 │
│  2. Click Send button                                      │
│  3. updateUserMessageFunc() - Add to messages state        │
│  4. callFastAPIRagAPIFunc() - Call API                     │
└───────────────┬───────────────────────────────────────────┘
                │
                │ HTTP GET /agent_chat?query=...
                ▼
┌───────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                                         │
│  1. Receive request                                        │
│  2. Get conversation history from SQLite                   │
│  3. Format messages                                        │
│  4. Call answering() from agent_gauss.py                   │
└───────────────┬───────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────┐
│  RAG AGENT (agent_gauss.py)                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ STEP 1: ROUTER                                      │  │
│  │  - Phân loại: TEXT_SEARCH / GRAPH_QUERY / etc      │  │
│  │  - Result: "TEXT_SEARCH"                           │  │
│  └─────────────────┬───────────────────────────────────┘  │
│                    │                                       │
│                    ▼                                       │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ STEP 2: SEARCH DATABASE                             │  │
│  │                                                      │  │
│  │  FAISS Vector Search:                               │  │
│  │  - Convert "Knox ID là gì?" → embedding vector      │  │
│  │  - Search similar vectors                           │  │
│  │  - Return: ["Knox ID là hệ thống...", ...]         │  │
│  │                                                      │  │
│  │  Neo4j Graph Search (if GRAPH_QUERY):               │  │
│  │  - Convert to Cypher query                          │  │
│  │  - Execute query                                    │  │
│  │  - Return graph results                             │  │
│  └─────────────────┬───────────────────────────────────┘  │
│                    │                                       │
│                    ▼                                       │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ STEP 3: CREATE CONTEXT                              │  │
│  │  Format context from search results:                │  │
│  │                                                      │  │
│  │  Context: """                                       │  │
│  │  Document 1: Knox ID là hệ thống quản lý...        │  │
│  │  Document 2: Knox ID hỗ trợ các tính năng...       │  │
│  │  """                                                │  │
│  └─────────────────┬───────────────────────────────────┘  │
│                    │                                       │
│                    ▼                                       │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ STEP 4: CALL LLM (Samsung Agent)                    │  │
│  │                                                      │  │
│  │  Payload:                                           │  │
│  │  {                                                  │  │
│  │    "context": "Document 1: ...",                   │  │
│  │    "question": "Knox ID là gì?"                    │  │
│  │  }                                                  │  │
│  │                                                      │  │
│  │  LLM Response (streaming):                          │  │
│  │  "K" → "no" → "x " → "ID " → "là " → ...          │  │
│  └─────────────────┬───────────────────────────────────┘  │
└────────────────────┼───────────────────────────────────────┘
                     │
                     │ Stream chunks
                     ▼
┌───────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                                         │
│  StreamingResponse - Forward chunks to frontend            │
└───────────────┬───────────────────────────────────────────┘
                │
                │ HTTP Response (streaming)
                ▼
┌───────────────────────────────────────────────────────────┐
│  FRONTEND (React)                                          │
│  1. Receive chunk: "K"                                     │
│  2. Update messages state: text = "K"                      │
│  3. Re-render UI → User sees "K"                           │
│                                                            │
│  4. Receive chunk: "no"                                    │
│  5. Update messages state: text = "Kno"                    │
│  6. Re-render UI → User sees "Kno"                         │
│                                                            │
│  ... (repeat until done)                                   │
│                                                            │
│  Final: "Knox ID là hệ thống quản lý thiết bị di động..." │
└───────────────┬───────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────┐
│  SAVE CONVERSATION                                         │
│  1. Frontend: saveConversationFunc()                       │
│  2. Backend: Save to SQLite                                │
│  3. Sidebar updates with new conversation                  │
└───────────────────────────────────────────────────────────┘
```

---

## 🎯 TÓM TẮT CỰC NGẮN

1. **User gõ** → React Frontend
2. **Frontend gọi** → FastAPI Backend
3. **Backend gọi** → RAG Agent
4. **Agent tìm** → FAISS/Neo4j
5. **Agent hỏi** → Samsung LLM
6. **LLM trả lời** → Stream về User

**Đơn giản thôi!** 😊

---

*Hy vọng diagram này giúp bạn hiểu rõ hơn!*
