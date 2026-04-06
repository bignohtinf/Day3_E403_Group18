# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Bùi Đức Tiến
- **Student ID**: 2A202600003
- **Date**: 22/05/2004

---

## I. Technical Contribution 
- **Modules Implementated**: src/agent.py (ReActAgent core loop)
Các hàm chính:
run() → vòng lặp ReAct
_parse_action() → parser action
_execute_tool() → thực thi tool
_extract_final_answer() → lấy kết quả cuối
- **Code Highlights**:
1. ReAct Loop (Core Logic)

for step in range(1, self.max_steps + 1):
    prompt = "\n".join(self.history)
    result = self.llm.generate(prompt, system_prompt=system_prompt)

Đây là nơi agent:
đọc history
suy nghĩ (LLM)
sinh hành động

2. Parse Action (quan trọng nhất)

func_style = re.search(r"Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)", text, re.DOTALL)

Cho phép agent:
hiểu format:
Action: tool_name(arguments)

3. Execute Tool: 

if hasattr(candidate, "execute"):

return str(candidate.execute(args))

if callable(candidate):

return str(candidate(args))

Hỗ trợ nhiều kiểu tool:
function
object
class

4. Logging + Metrics

logger.log_event("AGENT_STEP", {"step": step, "output": content})
tracker.track_request(...)

 Giúp:

debug
trace hành vi agent
- **Documentation**: Agent hoạt động theo đúng ReAct loop:

User → Thought → Action → Observation → Thought → ... → Final Answer
history lưu toàn bộ hội thoại
LLM dựa vào history để suy nghĩ bước tiếp theo
Tool được gọi khi cần external info

---

## II. Debugging Case Study 

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Agent không gọi tool mà trả lời trực tiếp hoặc sai format:
        Thought: I should search
Action: search

 Thiếu (arguments) → parser fail
- **Log Source**: PARSER_ERROR: Could not parse Action
- **Diagnosis**: Nguyên nhân:

Prompt chưa đủ chặt

LLM không tuân thủ format:

Action: tool_name(arguments)

Đây là lỗi phổ biến trong ReAct agent
- **Solution**: Cải thiện system prompt
Use EXACT action format: Action: tool_name(arguments)
Thêm fallback:
if not parsed:
    observation = "Could not parse Action..."

Giúp agent: tự sửa sai ở bước sau

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)


1.  **Reasoning**: Chatbot:
trả lời trực tiếp
không có reasoning rõ ràng
ReAct Agent:
có Thought
phân tích từng bước

 Ví dụ:

Thought: I need to extract text from PDF
Action: extract_text(file)

 → giúp:

minh bạch
dễ debug

2.  **Reliability**: Agent có thể kém hơn chatbot trong các trường hợp:

Lỗi format → không parse được
Tool fail → chain bị hỏng
Loop quá nhiều bước

 Chatbot:

đơn giản → ít lỗi hơn

3.  **Observation**: Observation đóng vai trò cực quan trọng:

Observation: extracted text...

 Agent dùng để: cập nhật trạng thái
quyết định bước tiếp theo

 Không có Observation → agent “mù thông tin”

---

## IV. Future Improvements (5 Points)


- **Scalability**: Sử dụng queue:
Celery / async worker
Cho tool chạy song song
- **Safety**: Thêm “Supervisor Agent”
kiểm tra action trước khi chạy
Validate input/output
- **Performance**: Dùng vector DB:
tìm tool phù hợp
Cache kết quả LLM

---


