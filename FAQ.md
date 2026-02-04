# ❓ CÂU HỎI THƯỜNG GẶP (FAQ)

## 📚 MỤC LỤC
1. [Câu hỏi về Kiến trúc](#câu-hỏi-về-kiến-trúc)
2. [Câu hỏi về Maintain](#câu-hỏi-về-maintain)
3. [Câu hỏi về Phát triển](#câu-hỏi-về-phát-triển)
4. [Câu hỏi Kỹ thuật](#câu-hỏi-kỹ-thuật)
5. [Câu hỏi về Deploy](#câu-hỏi-về-deploy)

---

## CÂUHỎI VỀ KIẾN TRÚC

### ❓ **1. Project này dùng để làm gì?**
**A:** RAG Chatbot - hệ thống chat AI có khả năng tìm kiếm và trả lời câu hỏi dựa trên knowledge base nội bộ công ty. Giống ChatGPT nhưng có data riêng của công ty.

---

### ❓ **2. RAG là gì? Khác gì với chatbot thường?**
**A:** 
- **Chatbot thường:** User hỏi → LLM trả lời (chỉ dựa vào kiến thức có sẵn)
- **RAG Chatbot:** User hỏi → Tìm kiếm context từ database → LLM + context → Trả lời chính xác hơn

**Ví dụ:**
- Hỏi: "Chính sách nghỉ phép của công ty?"
- Chatbot thường: Không biết (không có trong training data)
- RAG Chatbot: Tìm trong knowledge base công ty → Trả lời chính xác

---

### ❓ **3. Tại sao cần cả FAISS và Neo4j?**
**A:** Hai loại search khác nhau:

**FAISS (Vector Search):**
- Tìm kiếm theo **ngữ nghĩa** (meaning)
- Tốt cho: Tìm documents tương tự, semantic search
- Ví dụ: "Knox ID" sẽ tìm thấy "Samsung Knox Identity"

**Neo4j (Graph Database):**
- Tìm kiếm theo **relationships** (mối quan hệ)
- Tốt cho: Queries phức tạp về relationships
- Ví dụ: "User A có access tới documents nào?"

→ **Hybrid search** = Tốt nhất cả hai!

---

### ❓ **4. Samsung Agent là gì? Có thay được không?**
**A:** 
- Là LLM API của Samsung (internal)
- **CÓ thể thay thế bằng:**
  - OpenAI GPT-4 (trả phí)
  - Anthropic Claude (trả phí)
  - Ollama (free, chạy local)
  - Groq (free, fast)

**Cách thay:**
```python
# Thay vì Samsung Agent
response = call_samsung_agent(...)

# Dùng OpenAI
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    stream=True
)
```

---

### ❓ **5. Tại sao dùng SQLite thay vì MongoDB/PostgreSQL?**
**A:** 
- **SQLite:** Đơn giản, không cần server riêng, tốt cho small-medium scale
- **PostgreSQL/MySQL:** Tốt hơn cho production, nhiều users, concurrent access

**Khi nào cần migrate:**
- Khi có > 100 users concurrent
- Khi database > 1GB
- Khi cần replication/backup tốt hơn

---

## CÂU HỎI VỀ MAINTAIN

### ❓ **6. Tôi cần học những gì để maintain project này?**
**A:**
**Bắt buộc:**
- Python (FastAPI)
- JavaScript/React
- REST API basics
- SQL basics

**Nên học:**
- Vector databases (FAISS)
- Graph databases (Neo4j, Cypher)
- LangChain
- Docker

**Không cần ngay:**
- Machine Learning/AI (đã có sẵn models)
- DevOps advanced (trừ khi deploy production)

---

### ❓ **7. Có tài liệu nào giúp tôi hiểu nhanh hơn?**
**A:**
**Tài liệu đã có trong project:**
- `BAO_CAO_TONG_QUAN.md` - Tổng quan chi tiết
- `ARCHITECTURE_OVERVIEW.md` - Kiến trúc & flow
- `SETUP_GUIDE.md` - Hướng dẫn setup
- `COMMON_TASKS.md` - Các task thường gặp

**Tài liệu external:**
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- LangChain: https://python.langchain.com/
- FAISS: https://faiss.ai/
- Neo4j: https://neo4j.com/docs/

---

### ❓ **8. Làm sao biết feature nào đang broken?**
**A:**
**Checklist test nhanh:**
```bash
# 1. Backend health check
curl http://localhost:9000/active_users
# Nên trả về: {"count": 0}

# 2. Test chat
curl "http://localhost:9000/agent_chat?query=hello&userid=test&conid=123"
# Nên có response streaming

# 3. Test conversation save
curl -X POST http://localhost:9000/save_conversation \
  -H "Content-Type: application/json" \
  -d '{"id":"test","user_id":"test","title":"Test","messages":[],"lastUpdated":"2024-01-01","isPinned":false}'
# Nên trả về: {"message": "Conversation saved successfully"}

# 4. Frontend
# Mở http://localhost:5173
# Gõ message → Check response
```

---

### ❓ **9. Code này có tests không?**
**A:** **KHÔNG** (đây là điểm yếu).

**Cần làm:**
```python
# Tạo tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_active_users():
    response = client.get("/active_users")
    assert response.status_code == 200
    assert "count" in response.json()

def test_save_conversation():
    data = {
        "id": "test",
        "user_id": "test",
        "title": "Test",
        "messages": [],
        "lastUpdated": "2024-01-01",
        "isPinned": False
    }
    response = client.post("/save_conversation", json=data)
    assert response.status_code == 200
```

**Chạy tests:**
```bash
pip install pytest
pytest tests/
```

---

## CÂU HỎI VỀ PHÁT TRIỂN

### ❓ **10. Tôi muốn thêm tính năng upload file PDF/DOCX, có khó không?**
**A:** **KHÔNG khó!** 

**Đã có code upload .txt rồi, chỉ cần:**

```python
# Backend: main.py
from fastapi import File, UploadFile
import pypdf  # pip install pypdf

@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    content = ""
    
    if file.filename.endswith('.pdf'):
        # Read PDF
        pdf_bytes = await file.read()
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        content = "\n".join([page.extract_text() for page in reader.pages])
    
    elif file.filename.endswith('.docx'):
        # Read DOCX
        from docx import Document  # pip install python-docx
        doc_bytes = await file.read()
        doc = Document(io.BytesIO(doc_bytes))
        content = "\n".join([para.text for para in doc.paragraphs])
    
    elif file.filename.endswith('.txt'):
        content = (await file.read()).decode('utf-8')
    
    return {"filename": file.filename, "content": content}
```

**Frontend chỉ cần sửa:**
```javascript
// InputBar.jsx
<input
  type="file"
  accept=".txt,.pdf,.docx"  // Thêm .pdf, .docx
  onChange={handleFileChange}
/>
```

---

### ❓ **11. Có thể thêm authentication (login/logout) không?**
**A:** **CÓ!** Nhiều cách:

**Cách 1: JWT Token (khuyến nghị)**
```python
# pip install python-jose passlib
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])
SECRET_KEY = "your-secret-key"

@app.post("/login")
async def login(username: str, password: str):
    # Verify user
    user = verify_user(username, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Create token
    token = jwt.encode({"sub": user.id}, SECRET_KEY)
    return {"access_token": token}

@app.get("/protected")
async def protected(token: str = Header(...)):
    # Verify token
    payload = jwt.decode(token, SECRET_KEY)
    return {"user_id": payload["sub"]}
```

**Cách 2: OAuth2 (Google/Facebook login)**
```python
# pip install authlib
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='google',
    client_id='...',
    client_secret='...',
    # ...
)
```

---

### ❓ **12. Có thể thêm voice input/output không?**
**A:** **CÓ!**

**Voice Input (Speech-to-Text):**
```javascript
// Frontend
const recognition = new webkitSpeechRecognition();
recognition.onresult = (event) => {
    const text = event.results[0][0].transcript;
    setInputText(text);  // Điền vào input
};
recognition.start();
```

**Voice Output (Text-to-Speech):**
```javascript
// Frontend
const utterance = new SpeechSynthesisUtterance(botResponse);
speechSynthesis.speak(utterance);
```

**Hoặc dùng API tốt hơn:**
- OpenAI Whisper (STT)
- ElevenLabs (TTS)
- Google Cloud Speech

---

### ❓ **13. Làm sao để hệ thống handle nhiều users cùng lúc?**
**A:**

**Hiện tại:** SQLite + single server = OK cho ~100 users

**Scale lên:**
1. **Database:** SQLite → PostgreSQL
2. **Caching:** Thêm Redis
3. **Load Balancer:** Nginx
4. **Multiple Instances:** Docker Swarm/Kubernetes

```yaml
# docker-compose.yml
services:
  backend1:
    image: policybot-backend
    
  backend2:
    image: policybot-backend
  
  nginx:
    image: nginx
    # Load balance giữa backend1 và backend2
```

---

## CÂU HỎI KỸ THUẬT

### ❓ **14. Tại sao dùng streaming response thay vì response thường?**
**A:**

**Không streaming:**
```
User hỏi → Đợi 10s → Hiện toàn bộ câu trả lời
```
❌ UX tệ, user phải đợi lâu

**Có streaming:**
```
User hỏi → 0.1s: "K" → 0.1s: "no" → 0.1s: "x"...
```
✅ UX tốt, user thấy response ngay lập tức

**Code:**
```python
# Backend
async def generate():
    for chunk in response:
        yield chunk
        await asyncio.sleep(0.01)  # Simulate delay

return StreamingResponse(generate())

# Frontend
const reader = response.body.getReader();
while (true) {
    const {value, done} = await reader.read();
    if (done) break;
    updateUI(value);  // Update UI mỗi chunk
}
```

---

### ❓ **15. Context API (React) khác gì với Redux?**
**A:**

| Feature | Context API | Redux |
|---------|------------|-------|
| Complexity | Đơn giản | Phức tạp |
| Learning curve | Dễ | Khó |
| Boilerplate | Ít | Nhiều |
| DevTools | Không có | Có Redux DevTools |
| Middleware | Không có | Có (thunks, sagas) |
| Use case | Small-medium apps | Large apps |

**Khi nào dùng gì:**
- Project này: Context API (đủ rồi)
- Nếu app phức tạp hơn nhiều: Redux
- Alternative: Zustand (đơn giản hơn Redux)

---

### ❓ **16. FAISS index cần rebuild khi nào?**
**A:**

**Cần rebuild khi:**
- Thêm documents mới
- Xóa documents
- Update documents
- Thay đổi embedding model

**Cách rebuild:**
```bash
cd SuperAITech/agentic_rag
python src/indexing.py
```

**Tự động rebuild (nên làm):**
```python
# Tạo cron job rebuild hàng ngày
# crontab -e
0 2 * * * cd /path/to/project && python src/indexing.py
```

---

### ❓ **17. Làm sao biết agent đang "nghĩ" gì?**
**A:**

Code đã có `<think>` tag:
```python
# agent_gauss.py
def call_agent_stream(...):
    yield '<think>'  # Bắt đầu thinking
    # ... agent processing ...
    # Agent response sẽ có format:
    # <think>Tôi sẽ tìm kiếm trong database...</think>Câu trả lời là...
```

**Frontend parse:**
```javascript
// MessageContext.jsx
const thinkRegex = /<think>(.*?)<\/think>/s;
const match = fullRawStreamedContent.match(thinkRegex);

if (match) {
    extractedThinking = match[1];  // "Tôi sẽ tìm kiếm..."
    mainAnswer = content.replace(thinkRegex, "");  // "Câu trả lời là..."
}
```

**UI hiển thị:**
- ThinkingProcess.jsx - Component hiển thị thinking tab
- User có thể mở/đóng để xem agent "suy nghĩ" gì

---

## CÂU HỎI VỀ DEPLOY

### ❓ **18. Deploy lên đâu rẻ nhất?**
**A:**

**FREE Options:**
- **Vercel** - Frontend (miễn phí)
- **Railway** - Backend (free tier $5/month credit)
- **Render** - Backend (free tier với limitations)
- **Heroku** - Cả frontend+backend (free tier bị remove rồi)

**PAID Options (rẻ):**
- **DigitalOcean** - $5/month VPS
- **AWS EC2** - t2.micro ~$10/month
- **Google Cloud** - $5-10/month
- **Vultr** - $3.5/month

**Khuyến nghị cho beginner:**
```
Frontend: Vercel (free)
Backend: Railway (free $5 credit/month)
Database: Railway PostgreSQL (cùng plan)
Neo4j: Neo4j Aura (free tier)
```

---

### ❓ **19. HTTPS có cần thiết không? Setup thế nào?**
**A:** **CẦN THIẾT** cho production!

**Cách 1: Let's Encrypt (FREE)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto renew
sudo certbot renew --dry-run
```

**Cách 2: Cloudflare (FREE + CDN)**
1. Domain → Cloudflare nameservers
2. Cloudflare tự động cấp SSL
3. Bonus: CDN, DDoS protection, caching

---

### ❓ **20. Backup data như thế nào?**
**A:**

**SQLite (Conversations):**
```bash
# Manual backup
cp conversations.db conversations.backup.db

# Automatic daily backup
# crontab -e
0 3 * * * cp /path/to/conversations.db /path/to/backups/conv_$(date +\%Y\%m\%d).db

# Keep last 7 days only
0 4 * * * find /path/to/backups/ -name "conv_*.db" -mtime +7 -delete
```

**Neo4j:**
```bash
# Backup
neo4j-admin dump --database=neo4j --to=/backups/neo4j.dump

# Restore
neo4j-admin load --from=/backups/neo4j.dump --database=neo4j
```

**FAISS Index:**
```bash
# Just copy folder
cp -r SuperAITech/agentic_rag/data/faiss /backups/faiss_$(date +%Y%m%d)
```

---

## CÂU HỎI KHÁC

### ❓ **21. Tôi vừa join team, nên bắt đầu từ đâu?**
**A:**

**Week 1:**
1. Đọc `BAO_CAO_TONG_QUAN.md`
2. Đọc `ARCHITECTURE_OVERVIEW.md`
3. Follow `SETUP_GUIDE.md` để chạy local
4. Test tất cả features

**Week 2:**
1. Đọc code từng file (bắt đầu từ `main.py`)
2. Vẽ diagram flow cho mình hiểu
3. Thử break things (comment code xem chuyện gì xảy ra)
4. Đọc `COMMON_TASKS.md`

**Week 3:**
1. Fix 1 bug nhỏ (nếu có)
2. Thêm 1 feature nhỏ (ví dụ: thêm timestamp vào message)
3. Viết documentation cho phần mình làm

**Week 4+:**
1. Confident để maintain và develop
2. Có thể review code của người khác
3. Có thể trả lời câu hỏi của team

---

### ❓ **22. Có cần học AI/Machine Learning không?**
**A:** **KHÔNG BẮT BUỘC** cho maintain project này.

**Cần biết:**
- ✅ Concept cơ bản: RAG, embeddings, vector search
- ✅ Cách dùng APIs (OpenAI, HuggingFace)
- ✅ LangChain framework

**Không cần biết:**
- ❌ Training models từ đầu
- ❌ Math phức tạp (linear algebra, calculus)
- ❌ Deep learning internals

**Nếu muốn học sâu hơn:**
- Fast.ai course (free, practical)
- Andrew Ng ML course (Coursera)
- HuggingFace tutorials

---

### ❓ **23. Project này có phù hợp để học không?**
**A:** **CÓ!** Đây là project tốt để học vì:

✅ **Real-world architecture**
- Không phải toy project
- Production-ready structure
- Best practices (mostly)

✅ **Modern tech stack**
- React 19
- FastAPI
- RAG/AI integration

✅ **Full-stack**
- Learn cả frontend và backend
- Learn databases (SQL, Vector, Graph)
- Learn deployment

✅ **Scalable**
- Có thể mở rộng nhiều features
- Có thể optimize performance
- Có thể migrate technologies

---

### ❓ **24. Làm sao contact nếu cần support?**
**A:**

**Internal:**
1. Hỏi team members
2. Check documentation trong project
3. Search trong chat history/Slack

**External:**
1. FastAPI docs: https://fastapi.tiangolo.com/
2. React docs: https://react.dev/
3. LangChain Discord: https://discord.gg/langchain
4. Stack Overflow

**AI Assistants:**
1. ChatGPT
2. Claude
3. GitHub Copilot

---

### ❓ **25. Có nên refactor toàn bộ code không?**
**A:** **KHÔNG!**

**Big bang refactor = ❌ Nguy hiểm:**
- Tốn thời gian nhiều
- Rủi ro break features
- Khó test

**Incremental refactor = ✅ An toàn:**
- Refactor từng phần nhỏ
- Test sau mỗi thay đổi
- Ít rủi ro hơn

**Priority refactor:**
1. Fix critical issues (credentials, paths)
2. Add error handling
3. Add tests
4. Improve documentation
5. Refactor code smells (từ từ)

---

## 🎯 TÓM TẮT

✅ Project tốt, có thể maintain và develop  
✅ Không cần viết lại  
✅ Không cần biết AI/ML sâu  
✅ Có thể scale lên production  
✅ Phù hợp để học full-stack + AI  

**Bạn hoàn toàn có thể tự tin maintain project này!** 💪

---

*Nếu có câu hỏi khác, đừng ngần ngại hỏi team!* 🚀
