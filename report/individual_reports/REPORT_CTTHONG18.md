# Báo Cáo Cá Nhân: Lab 3 - Chatbot vs ReAct Agent

- **Họ và tên**: ctthong18
- **MSSV**: 2A202600014
- **Ngày**: 2026-04-06

---

## I. Đóng Góp Kỹ Thuật (15 Điểm)

Phần đóng góp chính của tôi là xây dựng cụm công cụ e-commerce để ReAct Agent có thể lấy dữ liệu bên ngoài và giải bài toán nhiều bước thay vì trả lời suy đoán.

- **Module đã triển khai**:
  - `src/tools/price_lookup.py`
  - `src/tools/check_stock.py`
  - `src/tools/get_discount.py`
  - `src/tools/calc_shipping.py`
  - `src/tools/web_search.py`
  - `src/tools/live_search_utils.py`
  - `src/tools/demo_data.py`
  - `src/tools/registry.py`
- **Bằng chứng commit**:
  - `bfc8c78` - `add tools` (thêm cụm tools cho phase agent)
  - `b211281` - `initial commit` (khung tool ban đầu)
- **Điểm nhấn mã nguồn**:
  - Thiết kế tool thống nhất theo `BaseTool` với `name`, `description`, `execute(...)`.
  - `price_lookup` và `check_stock` ưu tiên dữ liệu live từ URL mapping, fallback sang demo data khi không parse được.
  - `calc_shipping` tích hợp GHN API và có fallback khi thiếu biến môi trường.
  - `registry` tự động discover toàn bộ class kế thừa `BaseTool` trong `src/tools`.
- **Cách tương tác với ReAct loop**:
  - Agent sinh `Action: tool_name(arguments)` và gọi tool qua executor trong registry.
  - Kết quả tool được ghi vào `Observation` để vòng suy luận tiếp theo dùng làm ngữ cảnh.
  - Cơ chế này giúp giảm hallucination so với chatbot trả lời trực tiếp.

---

## II. Case Study Debugging (10 Điểm)

- **Mô tả vấn đề**: Agent bị kẹt `max_steps` ở các bài toán ngoài vùng coverage của tool (ví dụ Nintendo Switch OLED hoặc bundle keyboard/mouse).
- **Nguồn log**:
  - `logs/questions/20260406_154221_question_4.log`
  - `logs/questions/20260406_154221_question_5.log`
  - Dấu hiệu chính:
    - `Error: no live URL mapping configured for 'nintendo switch oled'. Supported products: iphone 15, macbook air m3.`
    - `Error: no live URL mapping configured for 'mechanical keyboard'...`
    - Có `PARSER_ERROR` ở question_4 khi model đi lệch format `Action/Final Answer`.
- **Chẩn đoán**:
  1. Coverage của `price_lookup`/`check_stock` còn hẹp do URL mapping đang hard-code ít sản phẩm.
  2. Khi tool liên tục trả lỗi unsupported, model thiếu chiến lược fallback phù hợp.
  3. Prompt strict format nhưng chưa đủ mạnh để ngăn drift hoàn toàn ở case phức tạp.
- **Giải pháp đã áp dụng**:
  - Bổ sung fallback demo data cho các tool để tránh dead-end khi live parsing thất bại.
  - Chuẩn hóa thông điệp lỗi để agent nhận biết rõ loại lỗi unsupported product.
  - Kết hợp cập nhật Agent v2: one-tool-per-step, retry theo observation, recovery hint khi chạm `max_steps`.

---

## III. Góc Nhìn Cá Nhân: Chatbot vs ReAct (10 Điểm)

1. **Khả năng suy luận**:
   - Chatbot baseline trả lời nhanh nhưng thiếu grounding.
   - ReAct tốt hơn nhờ chu trình `Thought -> Action -> Observation`, tách riêng bước thu thập dữ liệu và bước tính toán.

2. **Độ tin cậy**:
   - Agent có thể kém hơn chatbot khi tool chưa đủ coverage (sản phẩm chưa map), vì dễ loop đến `max_steps`.
   - Chatbot đôi khi đưa câu trả lời chung chung nhanh hơn, nhưng khó kiểm chứng và độ chính xác thấp.

3. **Vai trò của Observation**:
   - Observation là phản hồi môi trường quan trọng để agent tự điều chỉnh action kế tiếp.
   - Chất lượng observation càng rõ ràng thì agent càng dễ hội tụ về `Final Answer`.

---

## IV. Hướng Cải Tiến Tương Lai (5 Điểm)

- **Scalability**:
  - Mở rộng product normalization + catalog index để map linh hoạt tên sản phẩm thay vì hard-code URL.
  - Tách planner/executor cho bài toán tối ưu giỏ hàng nhiều ràng buộc.
- **Safety**:
  - Thêm schema validation cho arguments trước khi gọi tool.
  - Thêm cơ chế fail-fast khi gặp nhiều lỗi unsupported liên tiếp.
- **Performance**:
  - Cache kết quả web/tool theo query để giảm latency và token usage.
  - Áp dụng async I/O cho các tác vụ kiểm tra giá/tồn kho độc lập.

---

> [!NOTE]
> File report cá nhân đã được khôi phục và viết lại bằng tiếng Việt. Bạn chỉ cần cập nhật `Họ và tên` và `MSSV` đúng thông tin của mình trước khi nộp.
