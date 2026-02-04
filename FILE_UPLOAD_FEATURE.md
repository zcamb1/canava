# 📎 FILE UPLOAD FEATURE

## 🎯 Tổng quan

Feature cho phép user upload file .txt lên server, file sẽ được lưu theo conversation và nội dung được kết hợp với câu hỏi để gửi đến AI.

---

## 🔄 Flow hoạt động

```
1. User click nút 📎 (Attach)
   ↓
2. Chọn file .txt từ máy
   ↓
3. Frontend upload file lên server
   POST /conversation/{conversation_id}/upload_file
   ↓
4. Backend lưu file vào folder:
   conversation_uploads/{conversation_id}/{filename}
   ↓
5. Backend trả về:
   - filename
   - file_path
   - content (nội dung file)
   ↓
6. Frontend lưu file info và content
   Hiển thị preview: "📄 filename.txt (size) ✓ Uploaded"
   ↓
7. User nhập câu hỏi (hoặc không)
   Click Send
   ↓
8. Frontend combine:
   [File: filename.txt]
   
   Nội dung file:
   {file content}
   
   ---
   
   Câu hỏi: {user input}
   ↓
9. Gửi lên /agent_chat như bình thường
   ↓
10. AI xử lý với context từ file
```

---

## 🔧 Backend Implementation

### **Endpoint mới:**

```python
POST /conversation/{conversation_id}/upload_file
```

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: 
  - `file`: File object (.txt only)

**Response:**
```json
{
  "message": "File uploaded successfully",
  "filename": "document.txt",
  "file_path": "conversation_uploads/abc-123/document.txt",
  "content": "Nội dung file..."
}
```

**Errors:**
- `400`: Not a .txt file
- `500`: Server error

### **File storage:**
```
project/
└── conversation_uploads/
    ├── conversation_1/
    │   ├── file1.txt
    │   └── file2.txt
    ├── conversation_2/
    │   └── file3.txt
    └── ...
```

### **Code location:**
- `main.py` - Line ~330 (sau delete_specific_conversation endpoint)

---

## ⚛️ Frontend Implementation

### **1. Service API:**

**File:** `src/services/uploadAPI.js`

```javascript
import { API_BASE_URL } from "../config";

export async function uploadFileToConversation(conversationId, file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/conversation/${conversationId}/upload_file`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail);
  }

  return await response.json();
}
```

### **2. Component Updates:**

**File:** `src/components/chat/InputBar.jsx`

**States thêm:**
```javascript
const [isUploading, setIsUploading] = useState(false);
```

**Handler:**
```javascript
const handleFileChange = async (e) => {
  const file = e.target.files?.[0];
  if (file) {
    setIsUploading(true);
    
    try {
      const conversationId = currentConversationId || uuidv4();
      const response = await uploadFileToConversation(conversationId, file);
      
      setUploadedFile({
        name: response.filename,
        size: file.size,
        path: response.file_path
      });
      setFileContent(response.content);
    } catch (error) {
      alert(`Lỗi khi upload file: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  }
};
```

**UI Changes:**
- Hiển thị "⏳ Đang upload file..." khi `isUploading = true`
- Hiển thị "📄 filename.txt (size) ✓ Uploaded" khi upload xong
- Disable attach button khi đang upload

---

## 🧪 Testing

### **Backend Test:**

```bash
# Test upload endpoint
curl -X POST \
  http://localhost:9000/conversation/test-conv-id/upload_file \
  -F "file=@test.txt"

# Expected response:
{
  "message": "File uploaded successfully",
  "filename": "test.txt",
  "file_path": "conversation_uploads/test-conv-id/test.txt",
  "content": "Content of test.txt..."
}
```

### **Frontend Test:**

1. Mở app: http://localhost:5173
2. Click nút 📎
3. Chọn file .txt
4. Kiểm tra:
   - ✅ Hiện "Đang upload file..."
   - ✅ Sau đó hiện file preview với ✓ Uploaded
   - ✅ Console không có error
5. Nhập câu hỏi: "Tóm tắt nội dung file"
6. Click Send
7. Kiểm tra AI response có dựa vào file content không

---

## 🔒 Security Considerations

### **Current implementation:**

✅ **Đã có:**
- Chỉ accept file .txt
- File được lưu theo conversation_id (isolated)
- Validation filename trước khi save

⚠️ **Cần improve (future):**
- [ ] Giới hạn file size (max 10MB)
- [ ] Scan virus/malware
- [ ] Validate user có quyền access conversation không
- [ ] Rate limiting (max 10 files/conversation)
- [ ] Cleanup old files (>30 days)

### **Recommended improvements:**

```python
# 1. Add file size limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/conversation/{conversation_id}/upload_file")
async def upload_file_conversation(conversation_id: str, file: UploadFile = File(...)):
    # Check file size
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    with open(file_location, "wb") as buffer:
        while chunk := await file.read(chunk_size):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                os.remove(file_location)
                raise HTTPException(400, "File too large (max 10MB)")
            buffer.write(chunk)
```

```python
# 2. Add user authentication
@app.post("/conversation/{conversation_id}/upload_file")
async def upload_file_conversation(
    conversation_id: str, 
    file: UploadFile = File(...),
    user_id: str = Header(...)  # Require user_id in header
):
    # Verify user owns this conversation
    conv = await get_conversation_from_db(user_id, conversation_id)
    if not conv:
        raise HTTPException(403, "Access denied")
```

```python
# 3. Add cleanup job
import asyncio
from datetime import datetime, timedelta

async def cleanup_old_files():
    while True:
        # Delete files older than 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        for root, dirs, files in os.walk("conversation_uploads"):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) < cutoff_date.timestamp():
                    os.remove(file_path)
        
        await asyncio.sleep(24 * 60 * 60)  # Run daily

# Start cleanup task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_old_files())
```

---

## 📝 API Documentation

### **Updated OpenAPI/Swagger:**

Sau khi start backend, mở: http://localhost:9000/docs

Sẽ thấy endpoint mới:

```
POST /conversation/{conversation_id}/upload_file
  Parameters:
    - conversation_id (path, required): string
    - file (form, required): file
  
  Responses:
    200: File uploaded successfully
    400: Invalid file type
    500: Server error
```

---

## 🐛 Troubleshooting

### **Lỗi 1: "Failed to upload file: Network error"**

**Nguyên nhân:** Backend không chạy hoặc CORS issue

**Fix:**
```bash
# Check backend
curl http://localhost:9000/active_users

# Check CORS in main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    ...
)
```

### **Lỗi 2: "Only .txt files are supported!"**

**Nguyên nhân:** Chọn file không phải .txt

**Fix:** Chỉ chọn file có extension .txt

### **Lỗi 3: "Permission denied" khi save file**

**Nguyên nhân:** Backend không có quyền tạo folder

**Fix:**
```bash
# Create folder manually
mkdir conversation_uploads

# Or run backend with proper permissions
chmod 755 conversation_uploads
```

### **Lỗi 4: File upload nhưng AI không đọc được**

**Nguyên nhân:** Frontend không combine file content đúng

**Fix:** Check trong `handleSendMessage`:
```javascript
let finalPrompt = inputText.trim();
if (uploadedFile && fileContent) {
  finalPrompt = `[File: ${uploadedFile.name}]\n\nNội dung file:\n${fileContent}\n\n---\n\nCâu hỏi: ${inputText.trim()}`;
}
```

---

## 🚀 Future Enhancements

### **Short-term:**
- [ ] Support multiple files
- [ ] Support .pdf, .docx files
- [ ] File size limit UI indicator
- [ ] Progress bar for large files

### **Medium-term:**
- [ ] File preview in chat (before sending)
- [ ] Delete uploaded files
- [ ] List all files in conversation
- [ ] Download uploaded files

### **Long-term:**
- [ ] OCR for images
- [ ] Audio transcription
- [ ] Video analysis
- [ ] Automatic file summarization

---

## 📊 File Structure

```
project/
├── main.py                           # Backend endpoint
├── conversation_uploads/              # Uploaded files (gitignored)
│   └── {conversation_id}/
│       └── {filename}
├── src/
│   ├── services/
│   │   └── uploadAPI.js              # Upload service
│   └── components/
│       └── chat/
│           └── InputBar.jsx          # Upload UI
└── .gitignore                        # Exclude uploads folder
```

---

## ✅ Checklist Implementation

Backend:
- [x] Import shutil, File, UploadFile
- [x] Create POST /conversation/{conversation_id}/upload_file endpoint
- [x] Save file to conversation_uploads/{conversation_id}/
- [x] Return file info and content
- [x] Error handling

Frontend:
- [x] Create uploadAPI.js service
- [x] Update InputBar.jsx
- [x] Add isUploading state
- [x] Upload file on selection
- [x] Show uploading indicator
- [x] Show upload success with ✓
- [x] Combine file content with user input

Others:
- [x] Create .gitignore
- [x] Document feature

---

**Feature đã hoàn thành và ready để test!** 🎉
