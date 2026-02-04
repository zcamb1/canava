# 🔧 QUICK FIX - Module Not Found Error

## ❌ Lỗi hiện tại:
```
ModuleNotFoundError: No module named 'tiktoken'
```

## ✅ Cách fix:

### **Option 1: Cài tất cả packages (Khuyến nghị)**

```bash
# 1. Stop server hiện tại (nếu đang chạy)
# Nhấn CTRL+C

# 2. Activate virtual environment (nếu có)
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 3. Cài tất cả packages từ requirements.txt
pip install -r requirements.txt
```

### **Option 2: Cài chỉ package thiếu (Nhanh hơn)**

```bash
pip install tiktoken
```

**Nhưng sau đó bạn có thể gặp lỗi thiếu package khác!**

---

## 🚀 Sau khi cài xong:

```bash
# Chạy lại backend
python -m uvicorn main:app --reload --port 9000
```

**Nên thấy:**
```
INFO:     Uvicorn running on http://127.0.0.1:9000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
Loading diver, embedding model...
INFO:     Application startup complete.
```

---

## 📝 Nếu gặp lỗi khác:

### **Lỗi: "No module named 'transformers'"**
```bash
pip install transformers
```

### **Lỗi: "No module named 'langchain'"**
```bash
pip install langchain langchain-community langchain-core
```

### **Lỗi: "No module named 'faiss'"**
```bash
# CPU version (nhẹ hơn)
pip install faiss-cpu

# GPU version (nếu có NVIDIA GPU)
pip install faiss-gpu
```

### **Lỗi: "No module named 'neo4j'"**
```bash
pip install neo4j
```

### **Lỗi: "No module named 'markdownify'"**
```bash
pip install markdownify
```

---

## 🔍 Check packages đã cài:

```bash
# Xem tất cả packages
pip list

# Hoặc check package cụ thể
pip show tiktoken
pip show fastapi
pip show langchain
```

---

## ⚡ Nếu pip install chậm:

```bash
# Dùng mirror nhanh hơn (China mirror)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Hoặc (Aliyun mirror)
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

---

## 🐍 Nếu gặp lỗi version Python:

Project này cần **Python 3.10+**

```bash
# Check Python version
python --version

# Nếu < 3.10, download Python mới:
# https://www.python.org/downloads/
```

---

## 💡 Best Practice:

### **Tạo virtual environment (nếu chưa có):**

```bash
# Tạo venv
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Cài packages
pip install -r requirements.txt

# Chạy app
python -m uvicorn main:app --reload --port 9000
```

---

## 📊 Expected Output:

Khi chạy thành công, bạn sẽ thấy:

```
Loading diver, embedding model...
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:9000 (Press CTRL+C to quit)
```

Sau đó mở: http://127.0.0.1:9000/docs

Nên thấy Swagger UI với 11 endpoints.

---

## 🆘 Nếu vẫn không chạy được:

1. **Delete venv cũ và tạo lại:**
```bash
# Windows
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. **Upgrade pip:**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. **Check PYTHONPATH:**
```bash
# Windows
echo %PYTHONPATH%

# Linux/Mac
echo $PYTHONPATH

# Nếu có vấn đề, unset:
set PYTHONPATH=
```

---

**Chúc bạn fix thành công!** 🚀
