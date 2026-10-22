# VoiceOps 2026: ZentroMart Grounded Voice Support Agent

**LLM & Generative AI Capstone Project**  
*Consulting & Analytics Club, IIT Guwahati × Gnani.ai*

---

## 📌 Project Overview
VoiceOps 2026 is an end-to-end autonomous customer support agent engineered for **ZentroMart**, a fictional Indian online retailer. The agent handles customer calls through live speech telephony, maintains conversational context across turns, enforces identity verification gates before disclosing order details, and grounds all decisions in company policy documents using a hierarchical RAG pipeline.

---

## 🏗️ Architecture

```
Customer Audio ──► Gnani STT (en-IN) ──► Conversational Agent ──► Gnani TTS (Kaveri) ──► Audio Reply
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
         Knowledge Base (RAG)                                             Mock Tools
     - 21 Markdown policy docs                                      - lookup_order(order_id)
     - Hierarchical ranker (KB-00.1)                                - lookup_order(..., verification_value)
     - Business calendar (Mon-Sat, holidays)                        - create_ticket(summary, reason)
```

---

## 🚀 Quick Setup & Installation

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-username/zentromart-voiceops-2026.git
cd zentromart-voiceops-2026

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Credentials
Copy the `.env.example` file and insert your Gnani.ai API key:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GNANI_API_KEY=your_actual_gnani_api_key
```

---

## 🏃 Running the Agent

### A. Batch Telephony Runner (`run.py` / `run.sh`)
The official evaluation command processes a folder of audio files, runs the full agent pipeline on each, and saves speech outputs, text replies, and source citations:
```bash
./run.sh --input-dir /path/to/customer_audio --output-dir /path/to/output_replies
```

### B. Run Automated Benchmarks
```bash
# Evaluate Step 1 (Prompted Baseline) vs. Step 2 (Grounded RAG) on 52 practice questions:
python3 src/eval_questions.py

# Evaluate Step 3 (Multi-turn conversations & security gates) on 96 turns / 23 dialogues:
python3 src/eval_conversations.py
```

---

## 📊 Evaluation Scorecard Summary

| Metric | Step 1 (Baseline) | Step 2 (Grounded RAG) | Step 3 (Conversations) | Target Rubric |
| :--- | :---: | :---: | :---: | :---: |
| **Decision Accuracy** | 88.5% | **98.1%** | **100.0%** (96/96) | Grounded Answers (25) |
| **Retrieval Recall (Gold Evidence)** | N/A | **100.0%** (47/47) | **100.0%** | Retrieval Quality (15) |
| **Hard Negative Traps** | N/A | **0 violations** | **0 violations** | Retrieval Quality (15) |
| **Fact Precision (`must_include`)** | 11.5% | **96.2%** (50/52) | **100.0%** (96/96) | Grounded Answers (25) |
| **Security Verification Fidelity** | N/A | N/A | **100.0%** | Conversation Handling (20) |
| **Tool Calling Accuracy** | N/A | N/A | **100.0%** (96/96) | Conversation Handling (20) |

---

## 📂 Repository Structure

```
├── README.md               # Project documentation and setup guide
├── .env.example            # Environment configuration template
├── requirements.txt        # Python dependency manifest
├── run.py                  # Standalone batch audio runner
├── run.sh                  # Shell execution wrapper
├── report.pdf              # Official 4-page capstone technical report
├── demo_script.md          # 2-minute demo video script
├── src/                    # Core system package
│   ├── __init__.py
│   ├── kb_indexer.py       # Document chunker & metadata parser
│   ├── retriever.py        # FTS5 + precedence ranker + business calendar
│   ├── llm.py              # LLM generation layer (Step 1 baseline & Step 2 RAG)
│   ├── agent.py            # Step 3 multi-turn conversational state machine & tools
│   ├── voice.py            # Step 4 Gnani STT & TTS integration + text normalizer
│   ├── eval_questions.py   # Benchmark runner for Step 1 vs Step 2
│   └── eval_conversations.py # Benchmark runner for Step 3 multi-turn turns
└── sample_outputs/         # Benchmark evaluation outputs
    ├── step1_vs_step2_eval.json
    ├── step3_conversations_eval.json
    └── batch_run/
```
