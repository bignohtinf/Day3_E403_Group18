# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Group18
- **Team Members**: TBD
- **Deployment Date**: 2026-04-06

---

## 1. Executive Summary

This project upgrades a baseline chatbot into a ReAct-style e-commerce agent that can call real tools (price lookup, stock check, discount lookup, shipping calculation, calculator, and web search) with telemetry logging for each step.

- **Success Rate**: 40% strict success (2/5 test cases), 60% partial success (3/5) on `phase4_agent_v2_eval_20260406_154221.json`.
- **Key Outcome**: Compared to chatbot baseline, the agent produced tool-grounded answers with source links and explicit intermediate reasoning for price/tax workflows; baseline mostly returned generic or unverifiable responses for multi-step tasks.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
The implementation follows a strict loop in `ReActAgent`:
1. Build prompt from conversation history + system policy.
2. LLM returns either:
   - `Action: tool_name(arguments)`, or
   - `Final Answer: ...`
3. Agent parses action, executes one tool, appends `Observation`.
4. Repeat until final answer or `max_steps`.
5. Every step is logged (`AGENT_STEP`, `TOOL_CALL`, `LLM_METRIC`, `AGENT_END`) for traceability.

`ReActAgentV2` adds domain guardrails (only e-commerce), tighter tool constraints, and recovery hints on max-step failures.

### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `price_lookup` | `string` (product name) | Fetch/parse product prices from mapped store URLs, with fallback demo data. |
| `check_stock` | `string` (product name) | Infer in-stock/out-of-stock status from store pages, with fallback demo data. |
| `get_discount` | `string` (coupon code) | Search web snippets for discount percentages and summarize best observed discount. |
| `calc_shipping` | `string` (`"<weight_kg>, <destination>"`) | Calculate shipping fee via GHN API (or demo fallback if env not configured). |
| `calculator` | `string` (math expression) | Evaluate arithmetic expressions for totals, VAT, and final pricing. |
| `web_search` | `string` (query) | Perform DuckDuckGo-based web search and return top results/snippets/links. |

### 2.3 LLM Providers Used
- **Primary**: OpenAI `gpt-4o` (from `DEFAULT_PROVIDER=openai` and logged runs).
- **Secondary (Backup)**: Gemini `gemini-1.5-flash` (supported in provider factory), plus optional local GGUF model (`Phi-3-mini-4k-instruct`).

---

## 3. Telemetry & Performance Dashboard

Metrics are aggregated from per-question telemetry logs in `logs/questions/20260406_154221_question_*.log` (`LLM_METRIC` events, 27 total LLM calls):

- **Average Latency (P50)**: `1055 ms`
- **Max Latency (P99)**: `2446 ms` (nearest-rank p99 over 27 calls)
- **Average Tokens per Task**: `889.15` tokens per LLM call
- **Total Cost of Test Suite**: `$0.24007` (using project mock formula: `total_tokens/1000 * 0.01`)

Operational signal summary (same run):
- 5 questions processed, 23 tool calls, 1 parser error, 2 max-step recoveries (`V2_RECOVERY_HINT`).

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study: Tool coverage gap + parse fallback failure (Case 04)
- **Input**: Nintendo Switch cross-market comparison with FX conversion + import tax + VAT.
- **Observation**:
  - Early tool call returned: `Error: no live URL mapping configured for 'nintendo switch oled'. Supported products: iphone 15, macbook air m3.`
  - At step 7, model produced free-form plan text instead of `Action:`/`Final Answer`, triggering `PARSER_ERROR`.
  - Session ended with max-step timeout.
- **Root Cause**:
  1. Tool inventory is product-mapped and too narrow (only a small subset has live URL mapping).
  2. Prompt constraints are strict, but no robust fallback strategy exists when all relevant tools return unsupported-product errors.
  3. Parser depends on exact output format; once model drifts into narrative mode, loop loses progress.

### Case Study: Bundle planning complexity exceeds current tool granularity (Case 05)
- **Input**: 12 keyboards + 12 mice, multi-store stock checks, bulk discount, shipping optimization.
- **Observation**:
  - Multiple tool calls failed due to unsupported product names (`mechanical keyboard`, `... store mechanical keyboard`).
  - Agent kept iterating but could not form a valid, grounded plan before `max_steps`.
- **Root Cause**:
  1. No structured tool for basket optimization / split-order planning.
  2. Product normalization is weak (tool expects exact mapped keys).
  3. `max_steps=8` is insufficient for long-chain constrained planning without specialized planner state.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- **Diff**:
  - v2 system prompt adds strict policies: e-commerce-only scope, one-tool-per-step, retry-on-error, short web queries, and explicit final-answer format.
  - v2 agent adds out-of-domain blocker and recovery hint logging.
- **Result**:
  - Reliability improved for grounded tool usage in solvable mapped-product cases (e.g., Case 01 includes concrete source links and reproducible tax computation).
  - Trade-off: unsupported-product scenarios now fail explicitly (max-step) rather than returning speculative/hallucinated long-form answers.

### Experiment 2 (Bonus): Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Case 01 (price + tax) | Refused real-time data, no computed final from live stores | Returned cheapest store, links, and computed taxed total | **Agent** |
| Case 02 (shipping + discount) | Asked user for missing values | Produced end-to-end total (partly assumption-based) | **Agent** |
| Case 03 (stock + VAT) | Could not verify stock | Produced tool-assisted estimate with assumption note | **Agent** |
| Case 04 (FX import) | Generic guidance only | Timed out due to unsupported product + parser drift | Draw |
| Case 05 (bundle plan) | Hypothetical plan without verification | Timed out due to unsupported product mapping | Draw |

---

## 6. Production Readiness Review

- **Security**:
  - Tool inputs are partially sanitized (e.g., `calculator` restricts allowed characters; shipping validates numeric weight).
  - Needed next: stronger validation and schema-based argument parsing for all tools.
- **Guardrails**:
  - Current safeguards: `max_steps`, strict output format, domain gate, telemetry for parser/tool failures.
  - Needed next: confidence thresholds and fail-fast policy when repeated unsupported-product errors occur.
- **Scaling**:
  - Current architecture is linear ReAct loop with dynamic tool registry discovery.
  - Recommended evolution: planner-executor split (or graph-based orchestration) for complex multi-constraint tasks, plus broader product canonicalization and retrieval index.

---

> [!NOTE]
> Before submission, rename this file to `GROUP_REPORT_GROUP18.md` in this folder.
