import os
import re
import asyncio
import tiktoken
import sqlite3
import json
import uuid
import logging
import requests
from transformers import AutoTokenizer
from typing import List, Optional
from operator import itemgetter
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from uvicorn.logging import DefaultFormatter
from markdownify import markdownify as md
from SuperAITech.agentic_rag.src.agent.agent_gauss import answering, init

print('Loading diver, embedding model...')
embed_model, driver = init()

app = FastAPI(
    title="RAG Chatbot with Ollama and Conversation Memory (Streaming)",
    description="A simple RAG chatbot API using LangChain, Ollama, and ConversationSummaryBufferMemory with streaming responses.",
    version="1.0.0",
)

@app.get("/agent_chat", response_class=PlainTextResponse)
async def chat(query, userid, conid):
    conversation = await get_specific_conversation(userid, conid)
    conversation_history = []
    for mess in conversation.messages[:-1]:
        if mess.sender == 'user':
            conversation_history.append('Human: '+ mess.text)
        elif mess.sender == 'bot':
            conversation_history.append('AI: '+ mess.text)
    conversation_history = '\n'.join(conversation_history)
    return StreamingResponse(answering(embed_model, driver, query, conversation_history), media_type='text/plain') 

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic Models for API Requests ---
class Message(BaseModel):
    id: str
    sender: str
    text: str
    feedback: Optional[str] = None
    thinkingContent: Optional[str] = None
    isThinkingOpen: Optional[bool] = False
    isCopied: Optional[bool] = False
    isLiked: Optional[bool] = False
    isDisliked: Optional[bool] = False

class ConversationHistory(BaseModel):
    id: str
    user_id: str
    title: str
    messages: List[Message]
    lastUpdated: str
    isPinned: Optional[bool] = False

class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    question: str
    user_id: str
    conversation_id: str
    conversation_title: Optional[str] = None
    messages: List[Message]
    model: str

DATABASE_FILE = "conversations.db"

@app.post("/user_checkin/{user_id}")
async def user_checkin(user_id: str):
    """
    Endpoint for a user to signal they are active, storing the data in SQLite.
    """
    conn = get_db_connection()
    c = conn.cursor()
    # Using REPLACE INTO to either insert a new row or update an existing one
    c.execute("REPLACE INTO users (user_id, last_access) VALUES (?, ?)", (user_id, datetime.now()))
    conn.commit()
    conn.close()
    return {"message": "Checked in successfully"}

@app.get("/active_users")
async def get_active_users():
    """
    Endpoint to get the count of currently active users from SQLite.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Calculate the time threshold for active users (e.g., last 30 seconds)
    active_threshold = datetime.now() - timedelta(seconds=10)
    
    # Query the count of users whose last access was within the threshold
    c.execute("SELECT COUNT(user_id) FROM users WHERE last_access > ?", (active_threshold,))
    count = c.fetchone()[0]
    conn.close()
    
    return {"count": count}

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT,
            messages TEXT,
            last_updated TEXT,
            is_pinned INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            last_access TIMESTAMP NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS banned_users (
            user_id TEXT PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()
    print(f"SQLite database '{DATABASE_FILE}' initialized.")

@app.on_event("startup")
async def startup_event():
    init_db()

async def save_conversation_to_db(user_id: str, conversation_id: str, title: str, messages: List[dict], is_pinned: bool = False):
    """Saves or updates a conversation in the SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    messages_json = json.dumps(messages, ensure_ascii=False)
    last_updated = datetime.now().isoformat()
    # print(messages_json)
    cursor.execute("""
        INSERT OR REPLACE INTO conversations (id, user_id, title, messages, last_updated, is_pinned)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (conversation_id, user_id, title, messages_json, last_updated, int(is_pinned)))
    conn.commit()
    conn.close()
    print(f"Conversation '{conversation_id}' saved/updated locally for user '{user_id}'.")

async def get_conversation_from_db(user_id: str, conversation_id: str) -> Optional[ConversationHistory]:
    """Retrieves a single conversation from the SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, title, messages, last_updated, is_pinned FROM conversations WHERE user_id = ? AND id = ?", (user_id, conversation_id))
    row = cursor.fetchone()
    conn.close()
    if row:
        messages_data = json.loads(row["messages"])
        parsed_messages = [Message(**msg) for msg in messages_data]
        return ConversationHistory(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            messages=parsed_messages,
            lastUpdated=row["last_updated"],
            isPinned=bool(row["is_pinned"])
        )
    return None

async def get_all_conversations_for_user_from_db(user_id: str) -> List[ConversationHistory]:
    """Retrieves all conversations for a specific user, ordered by last_updated."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, title, last_updated, is_pinned FROM conversations WHERE user_id = ? ORDER BY last_updated DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    conversations = []
    for row in rows:
        conversations.append(ConversationHistory(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            messages=[],
            lastUpdated=row["last_updated"],
            isPinned=bool(row["is_pinned"])
        ))
    return conversations

async def delete_conversation_from_db(user_id: str, conversation_id: str):
    """Deletes a conversation for a specific user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE user_id = ? AND id = ?", (user_id, conversation_id))
    conn.commit()
    conn.close()
    print(f"Conversation '{conversation_id}' deleted for user '{user_id}'.")

@app.post("/rename_conversation", summary="Rename a conversation")
async def rename_conversation_endpoint(request: dict):
    user_id = request.get("user_id")
    conversation_id = request.get("conversation_id")
    new_title = request.get("new_title")

    if not all([user_id, conversation_id, new_title]):
        raise HTTPException(status_code=400, detail="Missing required fields: user_id, conversation_id, new_title")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE conversations SET title = ? WHERE user_id = ? AND id = ?", (new_title, user_id, conversation_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Conversation not found or user mismatch")
        return {"message": "Conversation renamed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rename conversation: {e}")
    finally:
        conn.close()

@app.post("/pin_conversation", summary="Pin or unpin a conversation")
async def pin_conversation_endpoint(request: dict):
    user_id = request.get("user_id")
    conversation_id = request.get("conversation_id")
    is_pinned = request.get("is_pinned")

    if not all([user_id, conversation_id, is_pinned is not None]):
        raise HTTPException(status_code=400, detail="Missing required fields: user_id, conversation_id, is_pinned")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE conversations SET is_pinned = ? WHERE user_id = ? AND id = ?", (int(is_pinned), user_id, conversation_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Conversation not found or user mismatch")
        return {"message": "Conversation pin status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update pin status: {e}")
    finally:
        conn.close()

@app.post("/generate_title", summary="Generate a concise title for conversation based on user question and bot's response")
async def generate_title_endpoint(request: TitleGenerationRequest):
    return {"title": str(datetime.now().strftime('%B %d %H:%M:%S'))}

@app.post("/save_conversation", summary="Save or update a full conversation")
async def save_conversation(conversation_history: ConversationHistory):
    """
    Endpoint to save or update a full conversation's history.
    This is called by the frontend after a message exchange.
    """
    try:
        await save_conversation_to_db(
            conversation_history.user_id,
            conversation_history.id,
            conversation_history.title,
            [msg.dict() for msg in conversation_history.messages],
            conversation_history.isPinned,
        )
        return {"message": "Conversation saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save conversation: {e}")    

@app.get("/conversations/{user_id}", response_model=List[ConversationHistory], summary="Get all conversations for a user")
async def get_user_conversations(user_id: str):
    """
    Endpoint to retrieve all conversations for a given user.
    """
    try:
        conversations = await get_all_conversations_for_user_from_db(user_id)
        return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversations: {e}")

@app.get("/conversation/{user_id}/{conversation_id}", response_model=Optional[ConversationHistory], summary="Get a specific conversation")
async def get_specific_conversation(user_id: str, conversation_id: str):
    """
    Endpoint to retrieve a specific conversation by ID for a given user.
    """
    try:
        conversation = await get_conversation_from_db(user_id, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation: {e}")

@app.delete("/conversation/{user_id}/{conversation_id}", summary="Delete a specific conversation")
async def delete_specific_conversation(user_id: str, conversation_id: str):
    """
    Endpoint to delete a specific conversation by ID for a given user.
    """
    try:
        await delete_conversation_from_db(user_id, conversation_id)
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {e}")