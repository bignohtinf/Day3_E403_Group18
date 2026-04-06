# Day 3 - Chatbot vs ReAct Agent (Group 18)

This repository contains our implementation of Lab Day 3, including:
- Chatbot baseline
- ReAct Agent v1
- Improved ReAct Agent v2
- Tooling, telemetry, evaluation scripts, and demo UI

## Setup

1. Create and activate virtual environment
2. Install dependencies
3. Configure `.env`

```bash
pip install -r requirements.txt
```

Required for cloud models:
- `OPENAI_API_KEY` or `GEMINI_API_KEY`

Optional for live shipping tool:
- `GHN_API_TOKEN`
- `GHN_SHOP_ID`
- `GHN_FROM_DISTRICT_ID`
- `GHN_TO_DISTRICT_MAP` (JSON string)

## What We Implemented

### Agent
- `src/agent/agent.py`: ReAct Agent v1 loop (Thought -> Action -> Observation)
- `src/agent/agent_v2.py`: Agent v2 with stronger policy and domain guard for e-commerce queries

### Tools
Current tools:
- `price_lookup`
- `check_stock`
- `get_discount`
- `calc_shipping`
- `calculator`
- `web_search`

Notes:
- Tools try live data first
- Fallback demo data is provided in `src/tools/demo_data.py` for stable classroom/demo runs

### Telemetry & Logs
- Structured logs in `logs/`
- Per-question logs in `logs/questions/` for Agent v2 evaluation/chat

## Run Scripts

### 1) Chatbot baseline (interactive)
```bash
python chatbot.py
```

### 2) Phase 1 tool demo
```bash
python phase1_tool_design_demo.py
```

### 3) Phase 2 baseline test cases
```bash
python phase2_chatbot_baseline.py
```

### 4) Agent v1 demo (interactive)
```bash
python phase3_agent_v1_demo.py
```

### 5) Agent v2 terminal chat (memory-style)
```bash
python phase4_agent_v2_chat.py
```

### 6) Agent v2 evaluation on 5 cases
```bash
python phase4_agent_v2_eval.py
```

### 7) Gradio UI
```bash
python ecommerce_wizard.py
```

## Suggested Demo Prompts

- "Find the cheapest iPhone 15 from 3 stores and calculate total for 2 units with 10% tax."
- "I want to buy 2 iPhones with code WINNER and ship to Hanoi. Compute final total."
- "Compare laptop gaming options under 25 million VND and recommend best value."

## Repository Structure (main parts)

- `src/agent/` - Agent implementations
- `src/tools/` - Tool implementations, registry, live parsing utilities, demo data
- `src/core/` - LLM provider abstractions and provider implementations
- `src/telemetry/` - Logging and metrics tracking
- `report/` - Group and individual report templates

---

This README reflects the current implementation status of Group 18 (including Agent v2 and demo UI).
