# 📝 CÁC TASK THƯỜNG GẶP & CÁCH THỰC HIỆN

## 🎯 MỤC LỤC
1. [Thêm API Endpoint Mới](#1-thêm-api-endpoint-mới)
2. [Sửa Bug Trong Chat](#2-sửa-bug-trong-chat)
3. [Thêm Feature Mới Ở Frontend](#3-thêm-feature-mới-ở-frontend)
4. [Update Knowledge Base](#4-update-knowledge-base)
5. [Deploy Production](#5-deploy-production)
6. [Debug Khi Có Lỗi](#6-debug-khi-có-lỗi)

---

## 1. THÊM API ENDPOINT MỚI

### **Ví dụ: Thêm endpoint `/get_user_stats`**

**File cần sửa:** `main.py`

```python
# Thêm vào main.py

@app.get("/get_user_stats/{user_id}")
async def get_user_stats(user_id: str):
    """
    Endpoint mới: Lấy thống kê của user
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query conversations count
    cursor.execute(
        "SELECT COUNT(*) FROM conversations WHERE user_id = ?", 
        (user_id,)
    )
    conv_count = cursor.fetchone()[0]
    
    # Query messages count
    cursor.execute(
        "SELECT messages FROM conversations WHERE user_id = ?", 
        (user_id,)
    )
    rows = cursor.fetchall()
    total_messages = sum(len(json.loads(row[0])) for row in rows)
    
    conn.close()
    
    return {
        "user_id": user_id,
        "total_conversations": conv_count,
        "total_messages": total_messages
    }
```

### **Frontend call API:**

**File: `src/services/userAPI.js`**

```javascript
export async function getUserStats(userId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/get_user_stats/${userId}`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching user stats:", error);
    return null;
  }
}
```

### **Test:**
```bash
# Terminal
curl http://localhost:9000/get_user_stats/test-user-id

# Browser console
fetch('http://localhost:9000/get_user_stats/test-user-id')
  .then(r => r.json())
  .then(console.log)
```

---

## 2. SỬA BUG TRONG CHAT

### **Ví dụ: Bug - Message không hiển thị đúng**

**Bước 1: Xác định scope**
```
Bug ở đâu?
[ ] Frontend không hiển thị
[ ] Backend không trả về
[ ] Agent không generate
```

**Bước 2: Check Frontend**

File: `src/context/MessageContext.jsx`

```javascript
// Thêm console.log để debug
const callFastAPIRagAPIFunc = async (userid, conid, prompt) => {
  console.log("📤 Sending:", { userid, conid, prompt });
  
  setIsLoading(true);
  // ... rest of code
  
  await callFastAPIRagAPI(userid, conid, prompt, signal, (chunk) => {
    console.log("📥 Received chunk:", chunk);  // DEBUG
    fullRawStreamedContent += chunk;
    // ... rest of code
  });
};
```

**Bước 3: Check Backend**

File: `main.py`

```python
@app.get("/agent_chat")
async def chat(query, userid, conid):
    print(f"📤 Received: query={query}, userid={userid}, conid={conid}")  # DEBUG
    
    conversation = await get_specific_conversation(userid, conid)
    print(f"💬 Conversation messages: {len(conversation.messages)}")  # DEBUG
    
    # ... rest of code
```

**Bước 4: Check Agent**

File: `SuperAITech/agentic_rag/src/agent/agent_gauss.py`

```python
def answering(embed_model, driver, similarity_search, ques, session_id, conversation):
    print(f"🤖 Agent received: {ques}")  # DEBUG
    
    r = router(driver, similarity_search, ques, session_id, conversation)
    print(f"🔀 Router result: {r}")  # DEBUG
    
    context = create_context(r)
    print(f"📄 Context length: {len(context)}")  # DEBUG
    
    # ... rest of code
```

**Bước 5: Fix & Test**
- Sửa code dựa trên logs
- Remove console.log/print sau khi fix xong

---

## 3. THÊM FEATURE MỚI Ở FRONTEND

### **Ví dụ: Thêm nút "Export Chat"**

**Bước 1: Tạo function export**

File: `src/utils/exportChat.js` (file mới)

```javascript
export function exportChatToText(messages, title) {
  let content = `Conversation: ${title}\n`;
  content += `Date: ${new Date().toLocaleString()}\n`;
  content += `\n${"=".repeat(50)}\n\n`;
  
  messages.forEach(msg => {
    const sender = msg.sender === 'user' ? 'You' : 'Bot';
    content += `${sender}: ${msg.text}\n\n`;
  });
  
  // Download file
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${title}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}
```

**Bước 2: Thêm nút vào UI**

File: `src/components/chat/ChatDisplay.jsx`

```javascript
import { exportChatToText } from '../../utils/exportChat';

function ChatDisplay({ chatDisplayRef }) {
  const { messages } = useMessage();
  const { currentConversationTitle } = useConversation();
  
  const handleExport = () => {
    exportChatToText(messages, currentConversationTitle);
  };
  
  return (
    <div>
      {/* Header với nút Export */}
      <div className="flex justify-between p-4">
        <h2>{currentConversationTitle}</h2>
        <button onClick={handleExport} className="btn">
          📥 Export
        </button>
      </div>
      
      {/* Rest of chat display */}
    </div>
  );
}
```

**Bước 3: Test**
- Click nút Export
- Check file tải về

---

## 4. UPDATE KNOWLEDGE BASE

### **Thêm documents mới vào RAG system**

**Bước 1: Chuẩn bị documents**
```bash
# Thêm file vào folder
cd SuperAITech/agentic_rag/data/documents/
# Copy các file .txt, .pdf, .docx vào đây
```

**Bước 2: Chạy indexing**

File: `SuperAITech/agentic_rag/src/indexing.py`

```python
# Nếu chưa có script, tạo mới:

from processing.doc_loader import load_documents
from processing.text_splitter import split_text
from embedding.embedding import get_embedding_model
import faiss
import pickle

def index_documents():
    # Load documents
    docs = load_documents("./data/documents/")
    
    # Split to chunks
    chunks = split_text(docs)
    
    # Get embeddings
    embed_model = get_embedding_model()
    vectors = [embed_model.get_text_embedding(chunk) for chunk in chunks]
    
    # Create FAISS index
    dimension = len(vectors[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)
    
    # Save
    faiss.write_index(index, "./data/faiss/index.faiss")
    with open("./data/faiss/chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)
    
    print(f"✅ Indexed {len(chunks)} chunks")

if __name__ == "__main__":
    index_documents()
```

**Bước 3: Chạy**
```bash
cd SuperAITech/agentic_rag
python src/indexing.py
```

**Bước 4: Restart backend**
```bash
# Ctrl+C để stop
# Chạy lại:
python -m uvicorn main:app --reload --port 9000
```

---

## 5. DEPLOY PRODUCTION

### **Option 1: Deploy lên VPS/Server**

**Bước 1: Chuẩn bị server**
```bash
# SSH vào server
ssh user@your-server.com

# Install dependencies
sudo apt update
sudo apt install python3.10 nodejs npm nginx neo4j
```

**Bước 2: Clone project**
```bash
git clone <repo-url>
cd project
```

**Bước 3: Setup Backend**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
nano .env
# (Thêm credentials)
```

**Bước 4: Setup Frontend**
```bash
npm install
npm run build  # Build production

# Serve với Nginx
sudo cp -r dist/* /var/www/html/
```

**Bước 5: Run Backend với PM2**
```bash
# Install PM2
npm install -g pm2

# Start backend
pm2 start "uvicorn main:app --host 0.0.0.0 --port 9000" --name policybot-backend

# Auto start on reboot
pm2 startup
pm2 save
```

**Bước 6: Setup Nginx**
```nginx
# /etc/nginx/sites-available/policybot

server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend
    location / {
        root /var/www/html;
        try_files $uri /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:9000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/policybot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### **Option 2: Deploy với Docker**

**Dockerfile.backend**
```dockerfile
FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
```

**Dockerfile.frontend**
```dockerfile
FROM node:18 AS build

WORKDIR /app
COPY package*.json .
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "9000:9000"
    env_file:
      - .env
    depends_on:
      - neo4j
  
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
  
  neo4j:
    image: neo4j:latest
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/password
```

**Deploy:**
```bash
docker-compose up -d
```

---

## 6. DEBUG KHI CÓ LỖI

### **Checklist Debug**

**1. Frontend Error:**
```javascript
// Check browser console (F12)
// Tìm error message

// Common errors:
- "Failed to fetch" → Backend không chạy
- "CORS error" → Backend thiếu CORS config
- "Cannot read property 'map' of undefined" → Data structure sai
```

**2. Backend Error:**
```bash
# Check terminal backend
# Tìm stack trace

# Common errors:
- "ModuleNotFoundError" → Thiếu package
- "Connection refused" → Neo4j/FAISS không chạy
- "KeyError" → Thiếu field trong data
```

**3. Agent Error:**
```python
# Check agent logs
# Print intermediate steps

def answering(...):
    print(f"Step 1: Router")
    r = router(...)
    print(f"Result: {r}")
    
    print(f"Step 2: Context")
    context = create_context(r)
    print(f"Context: {context[:100]}...")  # First 100 chars
    
    # ... rest
```

**4. Database Error:**
```bash
# Check Neo4j
# Browser: http://localhost:7474

# Check SQLite
sqlite3 conversations.db
> SELECT * FROM conversations;
> .exit
```

### **Debug Tools:**

**Frontend:**
- React DevTools (Chrome extension)
- Console.log()
- Debugger breakpoints

**Backend:**
- Print statements
- Pdb debugger: `import pdb; pdb.set_trace()`
- FastAPI logs

**Network:**
- Chrome DevTools → Network tab
- Postman/Insomnia for API testing

---

## 📝 TEMPLATE COMMIT MESSAGE

```
<type>: <subject>

<body>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

Examples:
feat: Add export chat feature
fix: Fix message streaming bug
docs: Update setup guide
```

---

## 🎯 CHECKLIST TRƯỚC KHI PUSH CODE

- [ ] Code chạy được local
- [ ] Đã test tất cả cases
- [ ] Xóa console.log/print debug
- [ ] Format code (prettier/black)
- [ ] Update documentation nếu cần
- [ ] Commit message rõ ràng
- [ ] Push lên branch riêng (không push master)

---

**Happy coding! 🚀**
