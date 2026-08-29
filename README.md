# 🤖 Autonomous Postman-to-Pytest Agent

An AI-powered Software Development Engineer in Test (SDET) workflow that dynamically generates, executes, and self-heals API test suites. 

This project demonstrates a complete local testing pipeline: it parses a Postman collection blueprint, utilizes a local Large Language Model (Ollama) to write `pytest` scripts, and executes those tests against a live local FastAPI backend with SQLite integration. If a test fails, the agent reads the traceback logs and rewrites the code until it passes.

## 🚀 Key Features

*   **Autonomous Test Generation:** Parses Postman JSON collections to dynamically write Python `requests`-based `pytest` functions.
*   **Self-Healing Execution Loop:** Automatically catches Pytest failures, feeds the error stack trace back to the LLM, and self-corrects the code (up to 3 retries).
*   **Live FastAPI Target:** Includes a functional local REST API (`GET`, `POST`) backed by a SQLite database to serve as the real-world testing target.
*   **Local AI Integration:** Powered by Ollama (Qwen/Llama) ensuring 100% data privacy and zero API costs.
*   **Interactive UI:** Built with Streamlit for a seamless drag-and-drop user experience and real-time execution logging.

## 🛠️ Tech Stack

*   **Backend API:** FastAPI, Uvicorn, Python
*   **Database:** SQLite
*   **AI / LLM:** Ollama (`qwen2.5-coder:7b` / `llama3`)
*   **Frontend / UI:** Streamlit
*   **Testing:** Pytest, Requests
*   **API Design:** Postman

## ⚙️ Local Setup & Installation

**1. Clone the repository**
```bash
git clone [https://github.com/YOUR-USERNAME/Postman_Pytest_automation.git](https://github.com/YOUR-USERNAME/Postman_Pytest_automation.git)
cd Postman_Pytest_automation

2. Set up the virtual environment & install dependencies

python -m venv venv
venv\Scripts\activate  # On Mac/Linux use: source venv/bin/activate
pip install fastapi uvicorn streamlit ollama pytest requests

3. Install Ollama & download the model
Download Ollama from ollama.com and pull the coder model:
ollama run qwen2.5-coder:7b


How to Run the Project
This project requires two terminal windows running simultaneously.

Terminal 1: Start the Target API
uvicorn main:app

Terminal 2: Start the AI Agent UI
streamlit run app.py
