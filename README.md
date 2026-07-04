# 🔍 GitHub Codebase RAG

An AI-powered tool that lets you "chat" with any public GitHub repository. Paste a repo link, and ask questions in plain English — the tool reads the actual code and answers using it, with source citations.

**🚀 Live app:** https://app-codebase-rag-ksztejjswebecc2s7ffs6.streamlit.app

## What it does
- Clones any public GitHub repo
- Reads and understands the code (Python files, Jupyter notebooks, etc.)
- Splits the code into chunks and converts them into embeddings (RAG pipeline)
- Stores embeddings in a vector database (ChromaDB)
- Answers your questions using only the actual code as context, with source file references

## Why I built it
Understanding a new codebase — at a job, in an open-source project, or reviewing a classmate's project — takes hours of manually reading files. This tool lets you ask direct questions instead, like "how does the login flow work?" or "what does this function do?", and get an answer grounded in the real code, not a guess.

## How to use it
1. Open the [live app](https://app-codebase-rag-ksztejjswebecc2s7ffs6.streamlit.app)
2. Paste your own free [Gemini API key](https://aistudio.google.com/apikey)
3. Paste any public GitHub repo URL
4. Click "Load Repo" and wait for indexing to finish
5. Ask any question about the code

## Tech stack
- Python
- Gemini API (embeddings + generation)
- ChromaDB (vector database)
- GitPython (repo cloning)
- Streamlit (web app + deployment)

## Example
> **Q:** What does the Netflix visualization notebook do?
> **A:** The notebook loads the Netflix titles dataset and generates several charts — Movies vs TV Shows count, top 10 countries by content, titles added per year, and top-rated genres.
