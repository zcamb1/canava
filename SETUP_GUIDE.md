# 🚀 HƯỚNG DẪN SETUP PROJECT

## 📋 YÊU CẦU HỆ THỐNG

### **Phần mềm cần cài:**
- ✅ Python 3.10+ 
- ✅ Node.js 18+ (với npm)
- ✅ Neo4j Database
- ✅ Git

### **Kiến thức cần có:**
- Biết dùng terminal/command line
- Hiểu cơ bản về Python và JavaScript
- Biết cơ bản về REST API

---

## 🔧 BƯỚC 1: CLONE PROJECT

```bash
cd "d:\that buon chan"
git clone <repository-url>  # Hoặc copy folder từ người khác
cd project
```

---

## 🐍 BƯỚC 2: SETUP BACKEND (Python)

### **2.1. Tạo virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### **2.2. Install dependencies**
```bash
pip install fastapi uvicorn
pip install neo4j
pip install llama-index
pip install llama-index-embeddings-huggingface
pip install langchain langchain-community langchain-openai langchain-ollama
pip install transformers
pip install faiss-cpu  # hoặc faiss-gpu nếu có GPU
pip install requests
pip install markdownify
pip install tiktoken
pip install python-multipart
```

**Hoặc tạo `requirements.txt`:**
```bash
pip freeze > requirements.txt
# Lần sau chỉ cần: pip install -r requirements.txt
```

### **2.3. Download Embedding Model**
```bash
# Model HaLong Embedding cần download trước
# Lưu vào: /path/to/halong_embedding/
# Hoặc dùng model khác từ HuggingFace
```

---

## 🗄️ BƯỚC 3: SETUP NEO4J DATABASE

### **3.1. Cài Neo4j**
- Download từ: https://neo4j.com/download/
- Hoặc dùng Docker:
```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/yourpassword \
    neo4j:latest
```

### **3.2. Tạo database**
1. Mở Neo4j Browser: http://localhost:7474
2. Login với username/password
3. Chạy lệnh tạo index (nếu cần)

### **3.3. Config trong code**
Sửa file `SuperAITech/agentic_rag/src/agent/agent_gauss.py`:
```python
NEO4J_URI = "bolt://localhost:7687"  # Thay đổi port nếu khác
NEO4J_USER = "neo4j"
NEO4J_PASS = "yourpassword"  # Thay password của bạn
```

---

## 🔍 BƯỚC 4: SETUP FAISS VECTOR DATABASE

### **4.1. Tạo FAISS index**
```bash
cd SuperAITech/agentic_rag/data
mkdir faiss

# Chạy indexing script
python ../src/indexing.py
```

### **4.2. Verify**
```bash
# Check nếu có file index trong folder faiss/
ls faiss/
# Nên thấy: index.faiss, index.pkl, etc.
```

---

## ⚛️ BƯỚC 5: SETUP FRONTEND (React)

### **5.1. Install dependencies**
```bash
cd "d:\that buon chan\project"
npm install
```

### **5.2. Config Backend URL**
Sửa file `src/config.js`:
```javascript
export const API_BASE_URL = "http://localhost:9000";  // Local backend
```

---

## 🔐 BƯỚC 6: FIX CRITICAL ISSUES (QUAN TRỌNG!)

### **6.1. Tạo file .env**
```bash
# Tạo file .env ở root project
touch .env  # Linux/Mac
# hoặc: New-Item .env  # Windows PowerShell
```

### **6.2. Thêm credentials vào .env**
```env
# .env file
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword

SAMSUNG_AGENT_URL=https://agent.sec.samsung.net/api/v1/run/...
SAMSUNG_API_KEY=sk-xxxxxxxxxxxxx

EMBED_MODEL_PATH=/path/to/halong_embedding/
DATABASE_DIR=./SuperAITech/agentic_rag/data/faiss
```

### **6.3. Update code để đọc .env**
Cài thêm:
```bash
pip install python-dotenv
```

Sửa `agent_gauss.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASS = os.getenv('NEO4J_PASSWORD')
```

### **6.4. Add .env vào .gitignore**
```bash
# .gitignore
.env
*.pyc
__pycache__/
venv/
node_modules/
```

---

## ▶️ BƯỚC 7: CHẠY PROJECT

### **7.1. Terminal 1 - Chạy Backend**
```bash
cd "d:\that buon chan\project"
venv\Scripts\activate  # Windows
python -m uvicorn main:app --reload --port 9000
```

**Kiểm tra:**
- Mở: http://localhost:9000/docs
- Nên thấy Swagger UI với 10 endpoints

### **7.2. Terminal 2 - Chạy Frontend**
```bash
cd "d:\that buon chan\project"
npm run dev
```

**Kiểm tra:**
- Mở: http://localhost:5173
- Nên thấy giao diện chatbot

---

## ✅ BƯỚC 8: TEST

### **8.1. Test Backend**
```bash
# Test /active_users endpoint
curl http://localhost:9000/active_users
# Nên trả về: {"count": 0}

# Test /agent_chat
curl "http://localhost:9000/agent_chat?query=hello&userid=test&conid=test123"
# Nên có response streaming
```

### **8.2. Test Frontend**
1. Mở trình duyệt: http://localhost:5173
2. Gõ câu hỏi: "Hello"
3. Kiểm tra:
   - ✅ Message hiển thị
   - ✅ Response streaming
   - ✅ Sidebar có conversation mới

---

## 🐛 TROUBLESHOOTING

### **Lỗi 1: "Module not found"**
```bash
# Fix: Cài lại package
pip install <package-name>
```

### **Lỗi 2: "Cannot connect to Neo4j"**
```bash
# Check Neo4j đang chạy:
# Windows: Services → Neo4j
# Linux: systemctl status neo4j
# Docker: docker ps | grep neo4j

# Fix: Start Neo4j
docker start neo4j
```

### **Lỗi 3: "CORS error"**
```python
# Check main.py có CORS config:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins
    ...
)
```

### **Lỗi 4: "FAISS index not found"**
```bash
# Fix: Chạy indexing
cd SuperAITech/agentic_rag
python src/indexing.py
```

### **Lỗi 5: "Frontend không gọi được Backend"**
- ✅ Check `src/config.js` có đúng URL backend?
- ✅ Check backend có đang chạy? (curl test)
- ✅ Check port có bị block?

---

## 📂 CẤU TRÚC SAU KHI SETUP

```
project/
├── .env                          ← Credentials (không commit)
├── .gitignore                    ← Git ignore file
├── main.py                       ← Backend server
├── conversations.db              ← SQLite database (tự tạo)
├── venv/                         ← Python virtual env
├── node_modules/                 ← Node modules
├── SuperAITech/
│   └── agentic_rag/
│       └── data/
│           └── faiss/            ← FAISS index files
├── src/                          ← Frontend source
└── BAO_CAO_TONG_QUAN.md         ← Documentation
```

---

## 🎯 CHECKLIST SETUP

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Neo4j installed và running
- [ ] Virtual environment created
- [ ] Python dependencies installed
- [ ] Embedding model downloaded
- [ ] FAISS index created
- [ ] .env file created với credentials
- [ ] Frontend dependencies installed
- [ ] Backend chạy được (port 9000)
- [ ] Frontend chạy được (port 5173)
- [ ] Test gửi message thành công

---

## 🚀 QUICK START (TL;DR)

```bash
# 1. Setup Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Setup Frontend
npm install

# 3. Create .env file
# (Thêm credentials như hướng dẫn trên)

# 4. Run Backend (Terminal 1)
python -m uvicorn main:app --reload --port 9000

# 5. Run Frontend (Terminal 2)
npm run dev

# 6. Open browser
# http://localhost:5173
```

---

## 📞 CẦN HỖ TRỢ?

1. Đọc file `TROUBLESHOOTING.md`
2. Check logs trong terminal
3. Hỏi team member
4. Google error message

**Good luck! 🍀**
