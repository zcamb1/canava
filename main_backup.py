import os
import re
import asyncio
import tiktoken
import sqlite3
import json
import uuid
import logging
from transformers import AutoTokenizer
from typing import List, Optional
from operator import itemgetter
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
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

os.environ["TOKENIZERS_PARALLELISM"] = "false"

class CustomModel(ChatOllama):
    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        tokenizer = None
        try:
            tokenizer = AutoTokenizer.from_pretrained('/home/nguyenluu/langchain_chatbot/base_models/bert-base-uncased')
        except Exception as e:
            print(e)
        if tokenizer:
            text = "".join([m.content for m in messages if m.content])
            return len(tokenizer.tokenize(text))
        else:
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
                num_tokens = 0
                for message in messages:
                    if message.content:
                        num_tokens += len(encoding.encode(message.content))
                return num_tokens
            except Exception as e:
                print(f"Warning: Could not use tiktoken for token counting ({e}). "
                    "Falling back to character-based approximation. "
                    "Accuracy for ConversationSummaryBufferMemory may be reduced.")
                total_chars = 0
                for message in messages:
                    if message.content:
                        total_chars += len(message.content)
                return total_chars // 4

def format_docs(docs: List[Document]) -> str:
    """Formats retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

print("Setting up RAG components...")
embeddings = HuggingFaceEmbeddings(model_name="/home/nguyenluu/base_models/multilingual-e5-small/")
doc_vectorstore = FAISS.load_local("faiss_small_v2/", embeddings, allow_dangerous_deserialization=True)

retriever = doc_vectorstore.as_retriever(search_kwargs={"k": 5})
print("RAG components ready.")
print("Initializing LLM (connecting to ollama)...")
gpt = CustomModel(
    model="gpt-oss:20b",
    openai_api_base="http://107.98.158.222:2604/v1",
    openai_api_key="ollama",
    max_tokens=2048,
    temperature=0.1,
    reasoning=True,
)
qwen3 = CustomModel(
    model="qwen3:1.7b",
    openai_api_base="http://107.98.158.222:2604/v1",
    openai_api_key="ollama",
    max_tokens=2048,
    temperature=0.1,
    reasoning=True,
)
deepseek = CustomModel(
    model="deepseek-r1:1.5b",
    openai_api_base="http://107.98.158.222:2604/v1",
    openai_api_key="ollama",
    max_tokens=2048,
    temperature=0.1,
    reasoning=True,
)
model_list = {
    "GPT": gpt,
    "Qwen3": qwen3,
    "DeepSeek": deepseek
}
print("LLM ready.")
# Hãy suy nghĩ từng bước một bằng tiếng Việt. Quy trình của bạn phải tuân theo cấu trúc sau: <think>Suy nghĩ từng bước một ở đây...</think>
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """<|im_start|>system
    Bạn đóng vai là một trợ lý ảo Tiếng Việt có tên là Polaris. Trợ lý ảo Polaris được sinh ra nhằm phục vụ mục đích trở thành một trợ lý ảo nhiệt tình, trung thực và luôn giải đáp các thắc mắc liên quan đến thông tin trong công ty Samsung SRV. Hãy đưa ra câu trả lời một cách thật chi tiết và hữu ích nhất có thể. 
    Chú ý các yêu cầu sau:
    - Nếu **có ngữ cảnh phù hợp** thì câu trả lời phải chính xác và đầy đủ theo ngữ cảnh đó và lưu ý chỉ sử dụng các thông tin có trong ngữ cảnh được cung cấp.
    - Ngoài ra, trong ngữ cảnh tôi cũng có một số _đề xuất các câu trả lời mẫu_ có thể liên quan, bạn có thể tham khảo thêm nếu cảm thấy phù hợp.
    - Nếu **không có ngữ cảnh phù hợp**, bạn có thể tự liên kết thêm các thông tin trong lịch sử hội thoại trước đó để trả lời câu hỏi. Nếu như vẫn không có ngữ cảnh phù hợp từ lịch sử trò chuyện, bạn phải từ chối trả lời và không giải thích thêm bất kì điều gì.
    - Ngoài ra, bạn có thể tự do trả lời các câu hỏi liên quan đến lời chào hỏi, hỏi thăm sức khỏe và giao tiếp cơ bản không liên quan đến chính sách công ty.
    <|im_end|>"""),
    MessagesPlaceholder("chat_history"),
    ("human", """<|im_start|>user
    Hãy trả lời câu hỏi dựa trên ngữ cảnh sau:
    ### Ngữ cảnh:
    {retrieved_docs}
    ### Câu hỏi:
    {question}
    <|im_end|>
    <|im_start|>assistant""")
])

def print_docs(x):
    print(x['retrieved_docs'])
    return x

print("RAG chain constructed.")

class EndpointFilter(logging.Filter):
    def __init__(self, prefixes: list[str], extra_block: list[str] = None):
        super().__init__()
        self.blocked_patterns = []
        
        # Prefix rules → match ANY method + prefix + UUID
        for prefix in prefixes:
            self.blocked_patterns.append(
                re.compile(fr'\"[A-Z]+ {prefix}{UUID_PATTERN}')
            )
        
        # Extra block rules (full regex applied directly)
        if extra_block:
            self.blocked_patterns += [re.compile(p) for p in extra_block]

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern in self.blocked_patterns:
            if pattern.search(msg):
                return False  # block this log
        return True

app = FastAPI(
    title="RAG Chatbot with Ollama and Conversation Memory (Streaming)",
    description="A simple RAG chatbot API using LangChain, Ollama, and ConversationSummaryBufferMemory with streaming responses.",
    version="1.0.0",
)

UUID_PATTERN = (
    r"[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}"
)

access_logger = logging.getLogger("uvicorn.access")
access_logger.addFilter(
    EndpointFilter(
        prefixes=[
            r"/user_checkin/",
        ],
        extra_block=[
            r'GET /active_users',
        ]
    )
)

for handler in access_logger.handlers:
    handler.setFormatter(
        DefaultFormatter(fmt="%(levelprefix)s [%(asctime)s] %(message)s", use_colors=True, datefmt="%Y-%m-%d %H:%M")
    )

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

class TitleGenerationRequest(BaseModel):
    """Request model for title generation endpoint."""
    user_question: str
    response_text: str

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
    """
    Endpoint to generate a concise title for a conversation based on the user's question and the AI's response.
    """
    user_question = request.user_question
    response_text = request.response_text

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert at summarizing conversations. Generate a concise, 3-5 words title for a conversation based on the user's question and the AI's response. The title should summarize the main topic of the conversation. Do not include any introductory phrases like 'Title:' or markdown formatting. Only return the title, do not generate thinking process."),
        ("human", f"User Question: \"{user_question}\"\nAI Response: \"{response_text}\"\nTitle:")
    ])

    title_chain = prompt_template | llm | StrOutputParser()

    try:
        generated_title = await title_chain.ainvoke({"user_question": user_question, "response_text": response_text})
        generated_title = generated_title.replace('"', '').replace("<think>", "").replace("</think>", "").strip()
        return {"title": generated_title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate title: {e}")

async def _run_background_memory_update(user_id: str, conversation_id: str, conversation_title: Optional[str], temp_memory):
    """
    Runs memory summarization and saves the updated conversation in a background task.
    """    

    temp_memory.prune()
    updated_history_from_memory = temp_memory.load_memory_variables({})['chat_history']

    message_to_save = []
    for msg in updated_history_from_memory:
        message_to_save.append({
            'id': msg.additional_kwargs.get('mess_id', str(uuid.uuid4())),
            'sender': msg.additional_kwargs.get('sender', 'system'),
            'text': msg.content,
            'feedback': msg.additional_kwargs.get('feedback', ''),
            'thinkingContent': msg.additional_kwargs.get('thinkingContent', ''),
            'isThinkingOpen': msg.additional_kwargs.get('isThinkingOpen', False),
            'isCopied': msg.additional_kwargs.get('isCopied', False),
            'isLiked': msg.additional_kwargs.get('isLiked', False),
            'isDisliked': msg.additional_kwargs.get('isDisliked', False),
        })
    await save_conversation_to_db(user_id, conversation_id, conversation_title, message_to_save, False)
    print("Background memory update complete.")

def html_to_markdown(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</?ul>", "", text)
    text = re.sub(r"<li>(.*?)</li>", r"- \1\n", text)
    return text

@app.post("/chat", summary="Send a message to the RAG chatbot and stream the response")
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    question = request.question
    user_id = request.user_id
    conversation_id = request.conversation_id
    conversation_title = request.conversation_title
    incoming_messages = request.messages 
    model_name = request.model

    llm = model_list[model_name]
    rag_chain = (
        {
            'question': itemgetter('question'),
            'chat_history': itemgetter('chat_history'),
            'retrieved_docs': itemgetter('question') | retriever | format_docs
        }
        # | RunnableLambda(print_docs)
        | rag_prompt
        | llm
        # | StrOutputParser()
    )
    existing_conversation = await get_conversation_from_db(user_id, conversation_id)
    existing_messages = []
    if existing_conversation:
        existing_messages = existing_conversation.messages

    full_response_content = ""
    full_thinking_content = ""
    history_prompt = PromptTemplate(input_variables=['new_lines', 'summary'], input_types={}, partial_variables={}, template="""Tóm tắt dần các dòng hội thoại được cung cấp, thêm vào bản tóm tắt trước đó và trả về một bản tóm tắt mới.\n\nVÍ DỤ\nTóm tắt hiện tại:\nNgười hỏi AI nghĩ gì về trí tuệ nhân tạo. AI cho rằng trí tuệ nhân tạo là một thế lực hướng đến điều tốt đẹp.\n\nCác dòng hội thoại mới:\nNgười hỏi: Tại sao bạn nghĩ trí tuệ nhân tạo là một thế lực hướng đến điều tốt đẹp?\nAI: Bởi vì trí tuệ nhân tạo sẽ giúp con người phát huy hết tiềm năng của mình.\n\nTóm tắt mới:\nNgười hỏi AI nghĩ gì về trí tuệ nhân tạo. AI cho rằng trí tuệ nhân tạo là một thế lực hướng đến điều tốt đẹp vì nó sẽ giúp con người phát huy hết tiềm năng của mình.\nHẾT VÍ DỤ\n\nTóm tắt hiện tại:\n{summary}\n\nCác dòng hội thoại mới:\n{new_lines}\n\nTóm tắt mới:""")
    temp_memory = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=2048,
        return_messages=True,
        memory_key="chat_history",
        prompt=history_prompt,
    )

    for msg in existing_messages:
        additional_kwargs = {
            'con_id': request.conversation_id,
            'user_id': request.user_id,
            'title': request.conversation_title,
            'model': request.model,
        }
        if msg.sender == 'user':
            additional_kwargs['sender'] = msg.sender
            additional_kwargs['mess_id'] = msg.id
            temp_memory.chat_memory.messages += [HumanMessage(content=msg.text, additional_kwargs=additional_kwargs)]
        elif msg.sender == 'bot':
            additional_kwargs['sender'] = msg.sender
            additional_kwargs['mess_id'] = msg.id
            additional_kwargs['thinkingContent'] = msg.thinkingContent
            additional_kwargs['isThinkingOpen'] = msg.isThinkingOpen
            additional_kwargs['isCopied'] = msg.isCopied
            additional_kwargs['isLiked'] = msg.isLiked
            additional_kwargs['isDisliked'] = msg.isDisliked
            additional_kwargs['feedback'] = msg.feedback
            temp_memory.chat_memory.messages += [AIMessage(content=msg.text, additional_kwargs=additional_kwargs)]
        elif msg.sender == 'system':
            additional_kwargs['sender'] = msg.sender
            temp_memory.chat_memory.messages += [SystemMessage(content=msg.text, additional_kwargs=additional_kwargs)]

    current_chat_history = temp_memory.load_memory_variables({})["chat_history"]
    # print("Chat history loaded into temporary memory for current turn:", current_chat_history)
    async def generate_and_stream():
        nonlocal full_response_content
        nonlocal full_thinking_content
        has_start_thinking = False
        try:
            chain_input = {
                "question": question,
                "chat_history": current_chat_history
            }
            streaming_content = rag_chain.astream(chain_input)

            async for chunk in streaming_content:
                thinking_content = chunk.additional_kwargs.get("reasoning_content", "")
                if thinking_content:
                    if not has_start_thinking:
                        yield "<think>"
                        has_start_thinking = True
                    full_thinking_content += thinking_content
                    yield thinking_content
                
                if chunk.content:
                    if has_start_thinking:
                        yield "</think>"
                    full_response_content += chunk.content
                    yield chunk.content
                    break
            
            async for chunk in streaming_content:
                if chunk.content:
                    full_response_content += chunk.content
                    # print(f'Org: {chunk.content}')
                    # print(f'convert: {html_to_markdown(chunk.content)}')
                    yield chunk.content
                
        except Exception as e:
            print(f"An error occurred during streaming: {e}")
            error_message = "I apologize, but I encountered an error during streaming."
            yield error_message
            full_response_content = error_message
        finally:
            additional_kwargs = {
                'con_id': request.conversation_id,
                'user_id': request.user_id,
                'title': request.conversation_title,
                'model': request.model,
                'sender': 'bot',
                'mess_id': str(uuid.uuid4()),
                'thinkingContent': '',
                'isThinkingOpen': False,
                'isCopied': False,
                'isLiked': False,
                'isDisliked': False,
                'feedback': '',
            }
            print(full_response_content)
            temp_memory.chat_memory.messages += [AIMessage(content=full_response_content, additional_kwargs=additional_kwargs)]
            background_tasks.add_task(
                _run_background_memory_update,
                user_id,
                conversation_id,
                conversation_title,
                temp_memory
            )

    return StreamingResponse(generate_and_stream(), media_type="text/plain")

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