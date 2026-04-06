# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Trần Lê Dũng
- **Student ID**: 2A202600296
- **Date**: 04/06/2026

---

## I. Technical Contribution (15 Points)

Trong khuôn khổ Lab 3, tôi đã triển khai và tích hợp các thành phần cốt lõi để xây dựng một hệ thống ReAct Agent có khả năng suy luận và sử dụng công cụ ngoại vi.

- `main.py` (entry point cho Phase 3 – ReAct Agent demo)  
- `src/agent/agent.py` (triển khai ReActAgent – core logic)  
- `src/tools/registry.py` (quản lý tool registry)  
- `chatbot.py` (build LLM provider)  

---

### Code Highlights

```python
llm = build_provider()
registry = build_registry()
agent = ReActAgent(
    llm=llm,
    tools=registry.as_agent_tools(),
    max_steps=5
)
```

Đoạn code trên thể hiện kiến trúc chính của hệ thống:

- `llm`: mô hình ngôn ngữ (GPT / local model)  
- `tools`: danh sách các tool có thể gọi  
- `max_steps`: giới hạn số vòng lặp của ReAct agent  

```python
answer = agent.run(user_input)
```

Đây là điểm kích hoạt ReAct loop:

- Input → `Thought` → `Action` → `Observation` → … → `Final Answer`

---

### Documentation (How it works)

Pipeline hoạt động như sau:

1. **User Input**  
   Ví dụ: `"I want to buy 2 iPhones..."`

2. **LLM (ReAct Prompt)**  
   Sinh ra:
   - `Thought`  
   - `Action`  

3. **Tool Execution**  
   Tool từ registry được gọi  

4. **Observation**  
   Nhận kết quả từ tool  

5. **Iterative Reasoning**  
   LLM đọc Observation và quyết định bước tiếp theo  

6. **Final Answer**  
   Khi agent dừng hoặc đạt `max_steps`  

👉 Đây chính là mô hình **ReAct (Reason + Act)**, khác với chatbot truyền thống (one-shot response).

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**:  
Agent bị lặp vô hạn khi gọi tool với input rỗng:

```text
Action: search(None)
```

- **Log Source**:

```text
Thought: I need to find iPhone price
Action: search(None)
Observation: Error - invalid input
Thought: Try again
Action: search(None)
...
```

- **Diagnosis**:  
Nguyên nhân chính:
- Prompt chưa rõ format Action  
- Tool schema không hướng dẫn input cụ thể  
- LLM không biết phải truyền gì vào tool  

=> Lỗi thuộc về **prompt design và tool specification**

- **Solution**:  

Cập nhật system prompt:

```text
Use Action: search("query string")
Never call tool with empty input
```

Thêm ví dụ vào prompt:

```text
Thought: I need price
Action: search("iPhone price")
```

=> Sau khi sửa:
- Agent gọi tool đúng  
- Không còn loop vô hạn  

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**:  
`Thought` giúp hiển thị quá trình suy luận của agent, từ đó:
- Dễ debug  
- Hiểu rõ agent đang làm gì  
- Kiểm soát hành vi tốt hơn  

Trong khi chatbot chỉ trả lời trực tiếp mà không có reasoning rõ ràng.

---

2. **Reliability**:  
Agent hoạt động kém hơn chatbot trong các trường hợp:
- Tool không ổn định  
- Prompt không rõ ràng  
- Task đơn giản  

Ví dụ:
- Hỏi kiến thức → chatbot tốt hơn  
- Task nhiều bước → agent tốt hơn  

---

3. **Observation**:  
Observation ảnh hưởng trực tiếp đến bước tiếp theo:

- Observation đúng → reasoning đúng  
- Observation sai → toàn bộ kết quả sai  

=> Agent thực chất là hệ thống:
**LLM + feedback loop từ môi trường**

---

## IV. Future Improvements (5 Points)

- **Scalability**:  
  - Sử dụng asynchronous queue cho tool calls  
  - Tách agent và tool thành microservices  

- **Safety**:  
  - Thêm "Supervisor LLM" để kiểm tra action  
  - Validate output trước khi trả về user  

- **Performance**:  
  - Sử dụng Vector DB để chọn tool phù hợp  
  - Cache kết quả tool  
  - Tối ưu prompt để giảm token usage  

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.