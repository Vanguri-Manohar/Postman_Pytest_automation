import streamlit as st
import json
import re
import subprocess
import os
import ollama

# --- PAGE CONFIG ---
st.set_page_config(page_title="API Test Gen Agent", layout="wide", page_icon="🤖")
st.title("🤖 Autonomous Postman-to-Pytest Agent")
st.markdown("Upload a Postman collection. The agent will write tests, execute them, and self-correct errors.")

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.header("⚙️ Agent Settings")
    model_choice = st.selectbox("Ollama Model", ["qwen2.5-coder:7b", "llama3", "codellama"])
    max_retries = st.slider("Max Self-Healing Retries", min_value=1, max_value=5, value=3)
    
# --- AGENT LOGIC ---
def extract_requests(items, extracted=None):
    if extracted is None:
        extracted = []
    for item in items:
        if "item" in item:
            extract_requests(item["item"], extracted)
        elif "request" in item:
            req = item["request"]
            url = req.get("url", "")
            if isinstance(url, dict):
                url = url.get("raw", "")
            extracted.append({
                "name": item.get("name", "Unnamed Request"),
                "method": req.get("method", "GET"),
                "url": url,
                "header": req.get("header", []),
                "body": req.get("body", {})
            })
    return extracted

def clean_llm_code(text):
    match = re.search(r'```python\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1)
    return text.replace("```", "")

def generate_code(requests_data, model):
    prompt = f"""
    You are an expert Python SDET. I have a JSON array of HTTP API requests from a Postman Collection.
    Write a complete Python `pytest` file using the `requests` library to test these endpoints.
    
    Requirements:
    1. import pytest, import requests
    2. Write a separate test function for each endpoint.
    3. Include assertions for status codes (e.g., assert response.status_code == 200 or 201).
    4. Return ONLY python code inside ```python blocks.
    
    Postman Data:
    {json.dumps(requests_data, indent=2)}
    """
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    return clean_llm_code(response['message']['content'])

def fix_code(broken_code, error_trace, model):
    prompt = f"""
    You are an expert Python debugging assistant. The following `pytest` file failed with errors.
    
    Failing Python code:
    ```python\n{broken_code}\n```
    
    Pytest Traceback:
    ```text\n{error_trace}\n```
    
    Analyze the error and fix the code. Return the COMPLETE, fixed Python code inside ```python blocks.
    """
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    return clean_llm_code(response['message']['content'])

# --- MAIN UI ---
uploaded_file = st.file_uploader("Upload Postman Collection (.json)", type=["json"])

if uploaded_file is not None:
    collection_data = json.load(uploaded_file)
    requests_data = extract_requests(collection_data.get("item", []))
    
    st.info(f"✅ Found {len(requests_data)} endpoints in collection.")
    
    if st.button("🚀 Start Generation & Testing Loop", type="primary"):
        test_filepath = "test_generated_api.py"

        try:
            status = st.status("🧠 Agent is thinking...", expanded=True)
            status.update(label="📝 Generating initial pytest suite...", state="running")
            current_code = generate_code(requests_data, model_choice)
            
            success = False
            final_logs = ""
            
            for attempt in range(1, max_retries + 1):
                status.update(label=f"🔄 Attempt {attempt}: Executing tests...", state="running")
                
                with open(test_filepath, 'w', encoding='utf-8') as f:
                    f.write(current_code)
                
                # Force local Pytest cache to avoid Windows permission errors
                result = subprocess.run(
                    ["pytest", test_filepath, "-v", "--tb=short", "-o", "cache_dir=.pytest_cache"], 
                    capture_output=True, text=True
                )
                
                final_logs = result.stdout + "\n" + result.stderr
                
                if result.returncode == 0:
                    status.update(label=f"✅ Success on attempt {attempt}! All tests passed.", state="complete")
                    success = True
                    break
                else:
                    status.update(label=f"⚠️ Attempt {attempt} failed. Analyzing errors and rewriting code...", state="running")
                    if attempt < max_retries:
                        current_code = fix_code(current_code, final_logs, model_choice)
                    else:
                        status.update(label=f"❌ Max retries ({max_retries}) reached.", state="error")
            
            st.divider()
            st.subheader("🎯 Final Results")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🐍 Generated Pytest Code")
                st.code(current_code, language="python")
                
            with col2:
                st.markdown("### 📋 Execution Logs")
                if success:
                    st.success("Tests Passed Successfully!")
                else:
                    st.error("Tests Failed.")
                st.code(final_logs, language="bash")

        finally:
            if os.path.exists(test_filepath):
                os.remove(test_filepath)