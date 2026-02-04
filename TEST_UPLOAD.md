# 🧪 TEST UPLOAD FEATURE (SIMPLE VERSION)

## 🎯 Chỉ cần test upload, không cần AI!

### **Bước 1: Cài 2 packages cơ bản thôi**

```bash
pip install fastapi uvicorn
```

### **Bước 2: Chạy test server**

```bash
python test_upload_server.py
```

**Sẽ thấy:**
```
🚀 Starting test server...
📎 Test upload at: http://localhost:9000/docs
INFO:     Uvicorn running on http://0.0.0.0:9000
```

### **Bước 3: Test bằng Swagger UI**

1. Mở: **http://localhost:9000/docs**
2. Click endpoint: `POST /conversation/{conversation_id}/upload_file`
3. Click "Try it out"
4. Nhập:
   - `conversation_id`: test-123
   - `file`: Chọn file .txt
5. Click "Execute"

**Kết quả:**
```json
{
  "message": "File uploaded successfully",
  "filename": "test.txt",
  "file_path": "conversation_uploads/test-123/test.txt",
  "content": "Nội dung file..."
}
```

### **Bước 4: Test với Frontend**

Frontend của bạn vẫn hoạt động như bình thường!

```bash
# Terminal 2
npm run dev
```

Mở: http://localhost:5173

Click 📎 → Chọn file → Upload thành công!

---

## 🔍 Test bằng curl (nếu muốn)

```bash
# Tạo file test
echo "This is a test file content" > test.txt

# Upload
curl -X POST \
  http://localhost:9000/conversation/test-123/upload_file \
  -F "file=@test.txt"
```

---

## ✅ Khi nào dùng cái gì?

| Server | Khi nào dùng | Có AI? |
|--------|-------------|--------|
| `test_upload_server.py` | Chỉ test upload | ❌ Không |
| `main.py` | Chạy full app với AI | ✅ Có |

---

## 📁 File structure

```
project/
├── test_upload_server.py    ← Server đơn giản (test only)
├── main.py                   ← Server đầy đủ (production)
├── conversation_uploads/     ← Folder lưu files
│   └── test-123/
│       └── test.txt
└── src/                      ← Frontend
```

---

## 🎉 Xong!

**Chỉ 2 lệnh là test được:**
```bash
pip install fastapi uvicorn
python test_upload_server.py
```

Không cần cài:
- ❌ Neo4j
- ❌ FAISS
- ❌ LangChain
- ❌ Transformers
- ❌ Embedding models

**Nhẹ nhàng!** 🚀
