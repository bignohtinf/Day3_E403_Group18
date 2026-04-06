# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Công Hùng
- **Student ID**: 2A202600140
- **Date**: 2026-04-06

---

## I. Đóng góp kỹ thuật (15 điểm)

Trong bài lab này, phần tôi phụ trách tập trung vào hai file chính là `chatbot.py` và `ecommerce_wizard.py`.

### 1. Các module đã thực hiện

- `chatbot.py`
- `ecommerce_wizard.py`

### 2. Nội dung đóng góp

#### a. Xây dựng baseline chatbot không dùng tool trong `chatbot.py`

Trong `chatbot.py`, tôi triển khai một baseline chatbot dạng CLI để làm mốc so sánh với ReAct Agent.

Các phần chính tôi thực hiện gồm:

- Viết hàm `build_provider()` để chọn backend theo biến môi trường `DEFAULT_PROVIDER`, hỗ trợ ba chế độ `openai`, `google/gemini` và `local`.
- Cho phép cấu hình model qua `DEFAULT_MODEL` để dễ hoán đổi giữa các nhà cung cấp mô hình mà không cần sửa code lõi.
- Xây dựng `run_demo()` cho phép chat trực tiếp trên terminal, có hỗ trợ `exit`, `quit`, `reset` và một prompt mẫu mặc định.
- Hiển thị thêm thông tin `prompt_tokens`, `completion_tokens` và `latency_ms` để phục vụ đánh giá hiệu năng của baseline.

Điểm quan trọng của file này là nó tạo ra một baseline “chatbot thường” không có tool, chỉ trả lời trực tiếp theo prompt hệ thống:

```python
system_prompt = (
    "You are a helpful chatbot. Answer directly with your best guess. "
    "You do not have external tools."
)
```

Thiết kế này giúp nhóm có một mốc so sánh rõ ràng với agent ở các tiêu chí như:

- độ chính xác,
- khả năng suy luận nhiều bước,
- khả năng lấy dữ liệu bên ngoài,
- token usage và latency.

#### b. Xây dựng giao diện hội thoại cho agent trong `ecommerce_wizard.py`

Trong `ecommerce_wizard.py`, tôi triển khai lớp giao diện thực hành cho ReAct Agent theo ngữ cảnh mua sắm điện tử.

Các phần chính tôi thực hiện gồm:

- Dùng `Gradio` để tạo giao diện chat thân thiện cho người dùng.
- Kết nối `build_provider()` từ `chatbot.py` với `ReActAgentV2` để agent có thể dùng cùng một cơ chế chọn model.
- Khởi tạo tool registry qua `build_registry()` và truyền các tool vào agent thông qua `_registry.as_agent_tools()`.
- Viết hàm `_build_context()` để ghép lịch sử hội thoại thành một prompt nhiều lượt, giúp agent duy trì ngữ cảnh qua các lượt chat liên tiếp.
- Viết `chat_fn()` để:
  - nhận câu hỏi mới,
  - gắn `run_id` và `question_id`,
  - ghi log theo từng lượt hỏi,
  - gọi `_agent.run(...)`,
  - cập nhật lại lịch sử hội thoại lên UI.
- Viết `reset_chat()` để tạo một phiên làm việc mới và reset bộ đếm câu hỏi.

Ngoài ra, tôi cũng hiển thị metadata của agent ngay trên giao diện như:

- model hiện tại,
- số bước tối đa (`max_steps`),
- danh sách tool đang được sử dụng.

Điều này giúp người dùng hiểu agent đang chạy trong cấu hình nào, đồng thời hỗ trợ demo dễ hơn trong lúc thuyết trình.

### 3. Điểm nhấn code

#### `chatbot.py`

- **Tách riêng logic chọn provider**: phần này giúp toàn bộ project dễ đổi backend giữa OpenAI, Gemini và local model.
- **Dùng cùng một interface `llm.generate(...)`**: điều này làm cho baseline chatbot và agent có thể dùng chung lớp provider.
- **In usage metrics trực tiếp sau mỗi lượt trả lời**: thuận tiện cho việc so sánh chi phí và tốc độ giữa chatbot và agent.

#### `ecommerce_wizard.py`

- **Tổ chức ngữ cảnh hội thoại nhiều lượt** bằng `_build_context()` thay vì chỉ gửi câu hỏi hiện tại.
- **Gắn logging context** theo `run_id` và `question_id` để truy vết lỗi theo từng câu hỏi.
- **Tách rõ phần UI và phần agent execution**: `Gradio` xử lý giao diện, còn logic suy luận vẫn nằm ở agent.

### 4. Mô tả cách code của tôi tương tác với ReAct loop

Code của tôi không trực tiếp cài đặt vòng lặp ReAct, nhưng đóng vai trò rất quan trọng trong việc đưa ReAct Agent vào sử dụng thực tế.

- `chatbot.py` tạo baseline không tool để so sánh với agent.
- `ecommerce_wizard.py` đóng vai trò “lớp ứng dụng” bọc bên ngoài ReAct Agent.
- Người dùng nhập câu hỏi trên UI, `chat_fn()` sẽ dựng lại ngữ cảnh hội thoại, gắn logging context, rồi chuyển prompt đó vào `_agent.run(...)`.
- Agent sau đó thực hiện chu trình Thought → Action → Observation → Final Answer và trả kết quả ngược lại cho giao diện.

Tóm lại, phần tôi làm giúp project có được cả hai mặt:

1. **một baseline chatbot để đánh giá**, và  
2. **một giao diện e-commerce wizard để trình diễn agent theo cách gần với sản phẩm thật hơn**.

---

## II. Case study debug (10 điểm)

### 1. Mô tả vấn đề

Một lỗi đáng chú ý mà tôi gặp trong quá trình làm `ecommerce_wizard.py` là lỗi **ngữ cảnh hội thoại bị nhiễu do format history từ Gradio không hoàn toàn khớp với format prompt mà agent mong đợi**.

Ở một số lượt chat tiếp theo, thay vì prompt có dạng gọn như:

- `User: ...`
- `Agent: ...`

thì trong log lại xuất hiện dữ liệu kiểu:

```text
User: [{'text': 'Tìm iPhone 15 rẻ nhất và tính tổng cho 2 máy + 10% thuế', 'type': 'text'}]
Agent: [{'text': 'The total cost for buying two iPhone 15s...', 'type': 'text'}]
```

Điều này làm prompt trở nên “bẩn”, vì agent không còn thấy lịch sử hội thoại dưới dạng văn bản tự nhiên mà phải đọc cả cấu trúc list/dict được serialize thành chuỗi.

### 2. Nguồn log

Một ví dụ rõ nằm trong log của phiên hỏi tiếp theo sau khi người dùng yêu cầu đổi ngôn ngữ sang tiếng Việt.

Prompt đầu vào chứa history ở dạng object serialize:

```text
User: [{'text': 'Tìm iPhone 15 rẻ nhất và tính tổng cho 2 máy + 10% thuế', 'type': 'text'}]
Agent: [{'text': 'The total cost for buying two iPhone 15s at the cheapest price from CellphoneS, including a 10% tax, is 38,918,000 VND.', 'type': 'text'}]
User: Hãy trả lời bằng tiếng Việt
```

Sau đó ở lượt tiếp theo, agent lại sinh ra một phản hồi lệch ý:

```text
Xin lỗi, tôi chỉ xử lý các yêu cầu liên quan đến mua sắm trực tuyến như giá cả, sản phẩm, khuyến mãi, vận chuyển,.. Hy vọng thông tin trên đã giúp bạn!
```

Phản hồi này không thực sự phù hợp với yêu cầu “hãy trả lời bằng tiếng Việt”, cho thấy context của agent đã bị ảnh hưởng bởi format hội thoại không sạch.

### 3. Chẩn đoán nguyên nhân

Nguyên nhân chính đến từ sự khác biệt giữa:

- format history mà `Gradio Chatbot` trả về,
- và format văn bản tuần tự mà `_build_context()` mong muốn.

Khi dữ liệu lịch sử không được chuẩn hóa hoàn toàn về chuỗi text thuần, prompt đầu vào của agent chứa nhiều cấu trúc thừa như `[{...}]`, làm mô hình khó nhận ra đâu là ý định thật sự của người dùng trong lượt mới.

Nói cách khác, lỗi không nằm hoàn toàn ở mô hình LLM mà nằm ở **lớp tích hợp UI → prompt builder**.

### 4. Cách khắc phục

Cách tôi xử lý là:

- chuẩn hóa history trước khi ghép vào prompt,
- đảm bảo mỗi lượt chỉ còn dạng text thuần,
- giữ cặp `User:` / `Agent:` nhất quán qua mọi turn,
- với các yêu cầu kiểu “trả lời bằng tiếng Việt”, có thể gộp preference ngôn ngữ vào câu hỏi hiện tại thay vì để agent phải suy luận từ một history bị nhiễu.

Nếu mở rộng tiếp, tôi sẽ bổ sung một hàm normalize riêng, ví dụ:

- nếu `content` là list/dict thì rút ra trường `text`,
- nếu `content` đã là string thì dùng trực tiếp,
- tuyệt đối không đưa raw object representation vào prompt.

### 5. Bài học rút ra

Case này cho tôi thấy một bài học quan trọng: trong hệ thống agent nhiều bước, lỗi không phải lúc nào cũng nằm ở prompt hay model. Chỉ cần lớp giao diện làm bẩn context, toàn bộ ReAct loop phía sau cũng có thể suy luận lệch.

Vì vậy, trong ứng dụng thực tế, phần **prompt construction và state management** quan trọng không kém gì phần model hay tool.

---

## III. Góc nhìn cá nhân: Chatbot vs ReAct (10 điểm)

### 1. `Thought` block giúp ích gì hơn so với chatbot trả lời trực tiếp?

Sự khác biệt lớn nhất giữa chatbot thường và ReAct Agent là khả năng chia bài toán thành từng bước nhỏ.

Ở `chatbot.py`, baseline được yêu cầu “trả lời trực tiếp với phỏng đoán tốt nhất” và không có tool. Điều này phù hợp với câu hỏi đơn giản, nhưng với các câu như:

- tìm giá rẻ nhất từ nhiều nơi,
- kiểm tra tồn kho,
- tính tổng tiền sau thuế, ship, coupon,

thì chatbot thường rất dễ đoán thiếu căn cứ hoặc gộp nhiều bước suy luận trong một lần trả lời.

Trong khi đó, ReAct Agent có `Thought` block để xác định:

- bước tiếp theo cần làm gì,
- có cần gọi tool hay không,
- sau khi có observation thì phải cập nhật kế hoạch ra sao.

Vì thế, `Thought` giúp quá trình suy luận minh bạch hơn, dễ debug hơn và giảm bớt việc mô hình “bịa” dữ liệu.

### 2. Khi nào agent lại tệ hơn chatbot?

Agent không phải lúc nào cũng tốt hơn chatbot. Trong quá trình làm lab, tôi thấy agent có thể kém hơn ở các tình huống sau:

- câu hỏi rất ngắn và đơn giản, không cần tool;
- history hội thoại bị lỗi format hoặc bị nhiễu;
- tool không hỗ trợ đúng sản phẩm/ngữ cảnh người dùng hỏi;
- agent phải qua nhiều bước nên latency cao hơn chatbot thường.

Ví dụ, với một yêu cầu chỉ là “hãy trả lời bằng tiếng Việt”, agent nhiều khi xử lý quá nặng hoặc hiểu sai context, trong khi chatbot thường có thể dịch hoặc trả lời lại ngắn gọn ngay lập tức.

Do đó, agent mạnh hơn trong các bài toán cần hành động nhiều bước, nhưng có overhead lớn hơn và nhạy cảm hơn với lỗi orchestration.

### 3. Observation ảnh hưởng gì đến bước tiếp theo?

Observation là điểm khác biệt cốt lõi giữa chatbot và agent.

Khi agent gọi tool và nhận về kết quả, nó không còn phải suy luận thuần túy từ xác suất ngôn ngữ nữa mà có thể dựa trên dữ liệu môi trường để quyết định bước tiếp theo.

Trong bài toán e-commerce, observation có thể là:

- giá sản phẩm từ store,
- kết quả kiểm tra tồn kho,
- chi phí vận chuyển,
- coupon hợp lệ hay không,
- kết quả tính toán từ calculator.

Các observation này giúp agent:

- điều chỉnh kế hoạch,
- xác minh thông tin trước khi kết luận,
- trả lời đáng tin cậy hơn chatbot baseline.

Nói ngắn gọn, chatbot chỉ “nghĩ”, còn agent vừa nghĩ vừa kiểm tra lại với môi trường.

---

## IV. Hướng cải tiến trong tương lai (5 điểm)

### 1. Khả năng mở rộng

Nếu phát triển thành hệ thống production, tôi sẽ tách phần tool execution ra khỏi luồng đồng bộ hiện tại và dùng kiến trúc bất đồng bộ hoặc queue-based.

Lý do là các tool như web search, inventory lookup hay shipping estimate có thể chậm và không nên chặn toàn bộ phiên hội thoại.

### 2. An toàn

Tôi sẽ bổ sung thêm lớp kiểm soát trước khi agent gọi tool, ví dụ:

- kiểm tra tool nào được phép gọi,
- validate đối số đầu vào,
- giới hạn những truy vấn ngoài phạm vi e-commerce,
- dùng một lớp supervisor hoặc rules-based checker để chặn action bất thường.

Điều này đặc biệt quan trọng nếu agent được tích hợp với API thật của doanh nghiệp.

### 3. Hiệu năng

Để tối ưu hiệu năng, tôi muốn cải tiến theo các hướng sau:

- cache kết quả tool cho các truy vấn lặp lại,
- chuẩn hóa memory/history trước khi đưa vào prompt,
- rút gọn context cũ bằng summarization,
- chỉ nạp các tool phù hợp với ngữ cảnh thay vì luôn nhồi toàn bộ tool list vào prompt.

Ngoài ra, với phần `ecommerce_wizard`, tôi cũng muốn thêm:

- lưu preference của người dùng như ngôn ngữ, khu vực, mức ngân sách,
- chế độ hiển thị trace Thought/Action/Observation để demo rõ hơn,
- bảng tổng hợp token usage và latency trực tiếp trên giao diện.

---
