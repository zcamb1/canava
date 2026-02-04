"""
Simple server to test file upload feature only
No RAG, no AI, just upload and echo back
"""
import os
import shutil
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Test Upload Server")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Test Upload Server is running!"}

@app.get("/active_users")
def get_active_users():
    """Mock active users endpoint"""
    return {"count": 1}

@app.post("/conversation/{conversation_id}/upload_file")
async def upload_file_conversation(conversation_id: str, file: UploadFile = File(...)):
    """
    Upload .txt file for testing
    """
    try:
        UPLOAD_DIR = f"conversation_uploads/{conversation_id}/"
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)
        
        file_location = f"{UPLOAD_DIR}/{file.filename}"
        
        # Check file type
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files are supported!")
        
        # Save file
        with open(file_location, "wb+") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read file content
        with open(file_location, "r", encoding="utf-8") as f:
            content = f.read()
        
        print(f"✅ File uploaded: {file_location}")
        print(f"📄 Content preview: {content[:100]}...")
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_path": file_location,
            "content": content
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")

@app.get("/test_chat")
async def test_chat(query: str, userid: str, conid: str):
    """Mock chat endpoint for testing"""
    return {
        "response": f"Echo: {query}",
        "user_id": userid,
        "conversation_id": conid
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting test server...")
    print("📎 Test upload at: http://localhost:9000/docs")
    uvicorn.run(app, host="0.0.0.0", port=9000)
