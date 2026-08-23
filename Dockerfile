# =====================================================
# Production AI Chatbot Docker Image
# =====================================================


FROM python:3.11-slim



# =====================================================
# Environment
# =====================================================


ENV PYTHONUNBUFFERED=1

ENV PYTHONDONTWRITEBYTECODE=1



WORKDIR /app



# =====================================================
# System Dependencies
# =====================================================


RUN apt-get update && apt-get install -y \

    build-essential \

    git \

    && rm -rf /var/lib/apt/lists/*



# =====================================================
# Install Python Dependencies
# =====================================================


COPY requirements.txt .



RUN pip install --upgrade pip



RUN pip install --no-cache-dir -r requirements.txt



# =====================================================
# Copy Application
# =====================================================


COPY . .



# =====================================================
# Create Required Directories
# =====================================================


RUN mkdir -p \

    data \

    uploads \

    logs \

    chroma_db



# =====================================================
# Streamlit Configuration
# =====================================================


EXPOSE 8501



# =====================================================
# Run Application
# =====================================================


CMD [

    "streamlit",

    "run",

    "app.py",

    "--server.address=0.0.0.0",

    "--server.port=8501"

]