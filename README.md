# 🤖 Production AI ChatBot

A production-level AI Assistant built using **LangGraph, LangChain, Google Gemini, RAG, and Agentic AI architecture**.

This chatbot intelligently decides the best way to answer user queries using:

- 🧠 Gemini LLM
- 📚 Retrieval Augmented Generation (RAG)
- 🌤 Real-time Weather Tool
- 📈 Stock Market Tool
- 🔎 DuckDuckGo Web Search
- ▶️ YouTube Video Summarization

The project follows a modular production architecture using Services, Graph Workflow, Tools, RAG Pipeline, and Streamlit UI.

---

# 🚀 Features

## 🧠 Intelligent AI Router (LangGraph)

The chatbot uses an LLM-powered router to decide which component should handle the user query.

Example:

```
User:
"What is the weather in Delhi?"

Router:
→ Weather Tool
```

```
User:
"Explain this PDF"

Router:
→ RAG Pipeline
```

```
User:
"Summarize this YouTube video"

Router:
→ YouTube Tool
```

---

# ✨ Main Features

## 1. Gemini AI Chat

Powered by:

- Google Gemini API
- LangChain ChatGoogleGenerativeAI

Capabilities:

- General conversation
- Coding assistance
- Explanation
- Reasoning
- Content generation


---

# 2. 📚 RAG Document Question Answering

Users can upload documents and ask questions.

Supported formats:

- PDF
- DOCX
- TXT


RAG Pipeline:

```
Document Upload

        ↓

Document Loader

        ↓

Text Splitter

        ↓

Embedding Generation

        ↓

Vector Database

        ↓

Retriever

        ↓

Gemini LLM

        ↓

Final Answer
```

Technologies:

- LangChain
- ChromaDB
- FAISS
- HuggingFace Embeddings
- Gemini


---

# 3. 🌤 Weather Tool

Provides real-time weather information:

- Temperature
- Weather condition
- Humidity
- Wind speed
- Forecast


Example:

```
"What is today's weather in Mumbai?"
```


---

# 4. 📈 Stock Market Tool

Provides financial information:

Supported:

- NSE
- BSE
- NASDAQ


Example:

```
"What is the current price of Tesla?"
```


---

# 5. 🔎 DuckDuckGo Search Tool

Used for:

- Latest news
- Current events
- Real-time information
- Web search


Example:

```
"Latest AI news"
```


---

# 6. ▶️ YouTube Summarizer

Features:

- Extract YouTube transcript
- Summarize videos
- Generate key points
- Answer questions from videos


Example:

```
"Summarize this YouTube video"
```


---

# 🏗️ System Architecture


```
                 User

                  |

                  |

            Streamlit UI

                  |

                  |

            Chat Service

                  |

                  |

          LangGraph Workflow

                  |

                  |

            AI Router Agent

                  |

 ------------------------------------------------

 |              |              |                |

Chat           RAG          Tools          Search

 |              |              |

Gemini     Vector DB      APIs

                  |

                  |

          Final Response

                  |

                  |

        SQLite Conversation Memory

```

---

# 📂 Project Structure


```
ChatBot/

│
├── app.py

├── README.md

├── requirements.txt

├── setup.py

├── Dockerfile


│
├── config/

│   ├── config.py

│   └── constants.py


│
├── core/

│   ├── logger.py

│   └── exception.py


│
├── graph/

│   ├── state.py

│   ├── router.py

│   ├── nodes.py

│   └── workflow.py


│
├── rag/

│   ├── rag_service.py

│   ├── loader_factory.py

│   ├── retriever_service.py

│   └── document_splitter.py


│
├── services/

│   ├── llm_service.py

│   ├── chat_service.py

│   ├── document_service.py

│   ├── conversation_service.py

│   └── checkpoint_service.py


│
├── tools/

│   ├── weather_tool.py

│   ├── stock_tool.py

│   ├── duckduckgo_tool.py

│   └── youtube_tool.py


│
└── ui/

    ├── styles.py

    ├── sidebar.py

    ├── chat.py

    ├── components.py

    └── utils.py

```

---

# 🛠️ Tech Stack


## Programming Language

- Python 3.11+


## Generative AI

- Google Gemini
- LangChain
- LangGraph


## RAG

- ChromaDB
- FAISS
- HuggingFace Embeddings


## Frontend

- Streamlit


## Database

- SQLite


## Monitoring

- LangSmith


## Deployment

- Docker
- HuggingFace Spaces
- Cloud Platforms


---

# ⚙️ Installation


## Clone Repository


```bash
git clone https://github.com/yourusername/ChatBot.git

cd ChatBot
```


---

## Create Virtual Environment


```bash
python -m venv venv
```


Activate environment:


Windows:

```bash
venv\Scripts\activate
```


Linux/Mac:

```bash
source venv/bin/activate
```


---

## Install Dependencies


```bash
pip install -r requirements.txt
```


---

# 🔑 Environment Variables


Create a file:

```
.env
```


Add:


```env
GOOGLE_API_KEY="your_gemini_api_key"


LANGSMITH_TRACING_V2=true

LANGSMITH_API_KEY="your_langsmith_api_key"

LANGSMITH_PROJECT="ChatBot"

```


---

# ▶️ Run Application


Start Streamlit:


```bash
streamlit run app.py
```


Open:


```
http://localhost:8501
```

---

# 🐳 Docker Deployment


Build image:


```bash
docker build -t ai-chatbot .
```


Run container:


```bash
docker run \
-p 8501:8501 \
--env-file .env \
ai-chatbot
```


---

# 🧪 Example Queries


## General AI Chat

```
Explain Transformers in simple words
```


## Document Question Answering

Upload PDF:

```
Summarize this document
```


```
What are the important points?
```


## Weather

```
Weather in Delhi today
```


## Stock

```
Tesla stock price
```


## Web Search

```
Latest AI trends
```


## YouTube

```
Summarize this video:
https://youtube.com/...
```


---

# 📊 LangSmith Monitoring


LangSmith tracks:

- LLM calls
- LangGraph workflow
- Tool execution
- RAG retrieval


Flow:


```
User Query

      ↓

Router

      ↓

Tool Selection

      ↓

Execution

      ↓

Gemini Response

      ↓

LangSmith Trace

```

---

# 🔐 Security Features


Implemented:

- Environment based API keys
- File validation
- Exception handling
- Logging system
- Thread isolation
- Modular architecture


---

# 🚀 Future Improvements


- Authentication
- User dashboard
- PostgreSQL integration
- Redis caching
- Multi-agent architecture
- Voice assistant
- Image understanding
- Kubernetes deployment


---

# 👨‍💻 Author


## Shravan Kumar Pandey


B.Tech Computer Science Engineering (Data Science)


Interested in:

- Data Science
- Machine Learning
- Generative AI
- LangChain
- LangGraph
- RAG Systems


---

# ⭐ Support


If you like this project, give it a ⭐ on GitHub.

```
