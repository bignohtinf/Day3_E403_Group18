# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: [Phùng Hữu Phú]
- **Student ID**: [2A202600283]
- **Date**: 2026-04-06
- **Repo**: https://github.com/bignohtinf/Day3_E403_Group18
---

## I. Technical Contribution (15 Points)

I focused on the full implementation path from baseline to Agent v2, then improved demo usability and documentation.

- **Modules Implemented / Updated**:
  - `chatbot.py`
  - `phase2_chatbot_baseline.py`
  - `phase1_tool_design_demo.py`
  - `src/tools/base_tool.py`
  - `src/tools/registry.py`
  - `src/tools/check_stock.py`
  - `src/tools/get_discount.py`
  - `src/tools/calc_shipping.py`
  - `src/tools/web_search.py`
  - `src/agent/agent_v2.py`
  - `phase4_agent_v2_chat.py`
  - `README.md` (project usage alignment after Agent v2 integration)
- **GitHub Evidence (commits)**:
  - `3344270` - add phase 1 tool registry and ecommerce tools
    - `phase1_tool_design_demo.py`
    - `src/tools/base_tool.py`, `src/tools/registry.py`, `src/tools/check_stock.py`, `src/tools/get_discount.py`, `src/tools/calc_shipping.py`, `src/tools/web_search.py`
  - `4882356` - chatbot baseline against 5 complex test cases
    - `phase2_chatbot_baseline.py`
  - `bbd7180` - The Hook: simple chatbot baseline
    - `chatbot.py`
  - `4d833e2` - add tools folder and example files
    - `src/tools/example.py`
  - `90d9999` - add Agent v2 and interactive chat runner
    - `src/agent/agent_v2.py`
    - `phase4_agent_v2_chat.py`
  - `8ab038f` - update `README.md` to reflect implemented workflow
- **Code Highlights**:
  - Built Phase 1 tooling foundation: tool interface, registry/autodiscovery, and e-commerce tool set for ReAct execution.
  - Implemented Phase 2 benchmarking script with multi-case chatbot baseline for failure observation.
  - Implemented Phase 3/4 progression by adding Agent v2 and interactive runner with memory-style UX.
  - Added stricter Agent v2 policy for ReAct behavior and e-commerce scope.
  - Added memory-style terminal chat runner for Agent v2 with question-level logging context.
  - Updated documentation to align with real run scripts and tooling status.
- **Documentation / Architecture Interaction**:
  - `chatbot.py` and `phase2_chatbot_baseline.py` provide baseline behavior/data for Chatbot vs Agent comparison.
  - Phase 1 tool registry (`src/tools/registry.py`) allows tool modules to plug into the same ReAct loop consistently.
  - `agent_v2.py` extends `ReActAgent` behavior and integrates with telemetry events (`AGENT_START`, `AGENT_STEP`, `AGENT_END`, `V2_RECOVERY_HINT`).
  - `phase4_agent_v2_chat.py` wraps Agent v2 into a practical demo loop (`You -> Dang suy nghi... -> Agent`) with contextual memory.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Agent v2 ended too early on task-oriented prompts due to direct-response fallback.
  - Example symptom: Agent returned planning text (no `Action:`) then immediately ended with `status=direct_response`.
- **Log Source**: `logs/2026-04-06.log` (entries around `question_2`, showing `AGENT_STEP` then `AGENT_END` with `direct_response`).
- **Diagnosis**:
  - The fallback condition in `agent.py` accepted any non-empty non-ReAct output as final direct response.
  - This rule was too broad and also captured unfinished task responses.
- **Solution**:
  - Narrowed fallback behavior to only short small-talk intents.
  - For task-oriented responses (contains markers like "first", "calculate", "search", "discount", etc.), Agent continues ReAct loop instead of ending early.
  - Result: casual greetings are handled gracefully, but e-commerce tasks still execute tool reasoning flow.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: ReAct provides explicit intermediate steps (`Thought -> Action -> Observation`) so the model can iteratively gather missing facts before answering.
2. **Reliability**: Agent can perform worse than chatbot when tool coverage is incomplete (missing product mappings, unavailable API credentials, weak parsing), causing retries or max-step timeouts.
3. **Observation**: Observations are the most important control signal. Good observations (clear tool outputs/errors) directly improve the next action choice and reduce hallucination.

---

## IV. Future Improvements (5 Points)

- **Scalability**:
  - Add async tool execution and caching for repeated lookups (price/stock queries).
  - Add structured tool response schema (JSON) to simplify parser robustness.
- **Safety**:
  - Add policy layer before execution to reject out-of-domain and unsafe requests deterministically.
  - Add output validator to prevent assumption-heavy final answers without evidence.
- **Performance**:
  - Add retrieval index for known stores/products to reduce unnecessary web search loops.
  - Add adaptive `max_steps` and early-stop heuristic based on confidence.

---

> [!NOTE]
> Rename this file to `REPORT_[YOUR_NAME].md` if your instructor requires strict naming format.
