%%writefile app.py
import streamlit as st
import git
import os
import shutil
import json
import tempfile
import google.generativeai as genai
import chromadb

st.set_page_config(page_title="GitHub Codebase RAG", page_icon="🔍")
st.title("🔍 GitHub Codebase RAG")
st.write("Paste a public GitHub repo link, then ask questions about the code.")

api_key = st.text_input("Enter your Gemini API key", type="password")
repo_url = st.text_input("GitHub repo URL", placeholder="https://github.com/user/repo")

if "collection" not in st.session_state:
    st.session_state.collection = None

def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start+chunk_size])
        start += chunk_size - overlap
    return chunks

if st.button("Load Repo") and api_key and repo_url:
    genai.configure(api_key=api_key)
    with st.spinner("Cloning repo..."):
        clone_dir = os.path.join(tempfile.gettempdir(), "streamlit_repo")
        if os.path.exists(clone_dir):
            shutil.rmtree(clone_dir)
        git.Repo.clone_from(repo_url, clone_dir)

    with st.spinner("Reading files..."):
        code_files = {}
        for root, dirs, files in os.walk(clone_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                filepath = os.path.join(root, file)
                if file.endswith('.ipynb'):
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            nb = json.load(f)
                        cells_text = []
                        for cell in nb.get('cells', []):
                            source = ''.join(cell.get('source', []))
                            if cell.get('cell_type') == 'code':
                                cells_text.append(f"# CODE CELL\n{source}")
                            elif cell.get('cell_type') == 'markdown':
                                cells_text.append(f"# MARKDOWN CELL\n{source}")
                        code_files[filepath] = '\n\n'.join(cells_text)
                    except Exception:
                        pass
                elif file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.md')):
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            code_files[filepath] = f.read()
                    except Exception:
                        pass

    with st.spinner(f"Embedding {len(code_files)} files..."):
        all_chunks = []
        for filepath, content in code_files.items():
            for i, chunk in enumerate(chunk_text(content)):
                all_chunks.append({"filepath": filepath, "chunk_id": i, "text": chunk})

        chroma_client = chromadb.Client()
        try:
            chroma_client.delete_collection("codebase_rag")
        except Exception:
            pass
        collection = chroma_client.create_collection(name="codebase_rag")

        for i, chunk in enumerate(all_chunks):
            embedding = genai.embed_content(
                model="models/gemini-embedding-001",
                content=chunk["text"],
                task_type="retrieval_document"
            )["embedding"]
            collection.add(
                ids=[f"chunk_{i}"],
                embeddings=[embedding],
                documents=[chunk["text"]],
                metadatas=[{"filepath": chunk["filepath"], "chunk_id": chunk["chunk_id"]}]
            )

        st.session_state.collection = collection

    st.success(f"Loaded and indexed {len(code_files)} files ({len(all_chunks)} chunks)!")

if st.session_state.collection:
    question = st.text_input("Ask a question about the code")
    if st.button("Ask") and question:
        with st.spinner("Thinking..."):
            q_embedding = genai.embed_content(
                model="models/gemini-embedding-001",
                content=question,
                task_type="retrieval_query"
            )["embedding"]

            results = st.session_state.collection.query(
                query_embeddings=[q_embedding],
                n_results=3
            )

            context = "\n\n---\n\n".join(results["documents"][0])
            prompt = f"""You are a helpful assistant answering questions about a codebase.
Use ONLY the following code context to answer. If the answer isn't in the context, say so.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            response = model.generate_content(prompt)

            st.markdown("### Answer")
            st.write(response.text)

            st.markdown("### Sources")
            for meta in results["metadatas"][0]:
                st.write(f"- {meta['filepath']} (chunk {meta['chunk_id']})")
