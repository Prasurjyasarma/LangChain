FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --upgrade pip setuptools wheel

# Install in careful order to avoid conflicts

# Step 1: Core scientific packages
RUN pip install --no-cache-dir \
    numpy==2.1.3 \
    pandas==2.2.3 \
    matplotlib==3.9.2 \
    seaborn==0.13.2

# Step 2: Basic utilities
RUN pip install --no-cache-dir \
    requests==2.32.3 \
    python-dotenv==1.0.1 \
    beautifulsoup4==4.12.3 \
    pypdf==5.1.0 \
    python-docx==1.1.2

# Step 3: Google AI SDK (specific compatible version)
RUN pip install --no-cache-dir \
    google-generativeai==0.8.0

# Step 4: LangChain core packages
RUN pip install --no-cache-dir \
    langchain==0.3.7 \
    langchain-community==0.3.7 \
    langchain-experimental==0.3.3 \
    langchain-text-splitters==0.3.0

# Step 5: LangChain Google integration (compatible with above)
RUN pip install --no-cache-dir \
    langchain-google-genai==2.0.3

# Step 6: Vector stores
RUN pip install --no-cache-dir \
    chromadb==0.5.20 \
    faiss-cpu==1.9.0

# Step 7: Additional tools
RUN pip install --no-cache-dir \
    google-search-results==2.4.2 \
    langsmith==0.1.143 \
    tiktoken==0.8.0

# Step 8: Jupyter (install last)
RUN pip install --no-cache-dir \
    notebook==7.3.1 \
    jupyterlab==4.3.3

# Step 9: Streamlit UI ✅ ADD THIS
RUN pip install --no-cache-dir \
    streamlit==1.39.0

# Copy the entire project
COPY . .

# Expose ports
EXPOSE 8888
EXPOSE 8501 

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]