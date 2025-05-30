# Multi-Format Autonomous AI System with Contextual Decisioning & Chained Actions

## Demonstration Video
[link](https://drive.google.com/file/d/1EqCw1K8q-4dbYUXa1JyUxDo-UCQRhvUr/view?usp=drive_link)

## 🔥 Project Overview

This system is a multi-agent architecture capable of processing inputs from Emails, PDFs, and JSON webhooks. It uses classification to route inputs to specialized agents and dynamically triggers follow-up actions based on content analysis.

### 🧠 Core Agents

* **Classifier Agent**

   * Detects input format: `Email`, `JSON`, `PDF`
   * Detects business intent: `RFQ`, `Complaint`, `Invoice`, `Regulation`, `Fraud Risk`
   * Uses few-shot examples + LangChain/OpenAI

* **Email Agent**

   * Extracts: `sender`, `urgency`, `issue/request`
   * Analyzes tone: `angry`, `polite`, `escalation`
   * Routes:

      * Urgent & angry → `POST /crm/escalate`
      * Routine → Log and close

* **JSON Agent**

   * Validates incoming JSON schema
   * Flags anomalies: type mismatches, missing fields
   * Alerts logged via memory or `POST /risk_alert`

* **PDF Agent**

   * Parses invoices or policies
   * Flags:

      * Invoices > 10,000
      * Mentions of compliance terms like `GDPR`, `FDA`

* **Shared Memory Store (SQLite)**

   * Stores:

      * Input metadata (source, timestamp)
      * Agent outputs and extracted fields
      * Triggered actions and decision traces

* **Action Router**

   * Analyzes agent outputs
   * Triggers simulated actions via REST:

      * `/crm/escalate`
      * `/risk_alert`
   * Includes retry logic and logs results

---

## 🧰 Tech Stack

* **Language**: Python 3.10+
* **Framework**: FastAPI
* **LLM & Routing**: LangChain + OpenAI
* **PDF Parsing**: PyPDF2
* **Database**: SQLite
* **Shared Memory**: File-based SQLite
* **API Calls**: `requests` library

---

## 🐳 Running the System (via Docker Compose)

1. Clone the repository:

   ```bash
   git clone https://github.com/rohit83r/multi-agent-system
   cd multi-agent-system
   ```

2. Build and run all services:

   ```bash
   docker-compose up --build
   ```

3. Access endpoints:

   * API Sim: [http://localhost:8000](http://localhost:8000)
   * UI : open index.html in browser 

---

## 📁 Directory Structure

```
multi-agent-system/
├── agents/
│   ├── classifier.py
│   ├── email_agent.py
│   ├── json_agent.py
│   ├── pdf_agent.py
├── utils/
│   └── memory.py
├── router/
│   └── action_router.py
├── main.py (FastAPI app)
├── ui/
│   └── index.html
├── docker-compose.yml
├── Dockerfile
├── README.md
├── sample_inputs/

```

---

## 📄 Sample Inputs

* `sample_email.txt` (urgent, angry tone)
* `sample.json` (webhook event)
* `invoice.pdf`, `policy.pdf`

---

## ✅ Output Examples

* Classification Logs (SQLite)
* REST Logs (action trace)
* Screenshots of agent output decisions

---
