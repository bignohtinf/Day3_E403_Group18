# Báo Cáo Nhóm: Lab 3 - Hệ Thống Agentic Mức Production

- **Tên Nhóm**: Group18
- **Thành Viên**: Chu Thành Thông 2A202600014, Nguyễn Công Hùng 2A202600140, Bùi Đức Tiến 2A202600003, Phùng Hữu Phú 2A202600283, Trần Lê Dũng 2A202600296
- **Ngày Triển Khai**: 2026-04-06

---

## 1. Tóm Tắt Điều Hành

Dự án nâng cấp chatbot baseline thành agent ReAct cho bài toán e-commerce, có thể gọi tool thực tế (tra giá, kiểm tra tồn kho, tìm mã giảm giá, tính phí vận chuyển, máy tính, tìm kiếm web) và ghi telemetry ở từng bước suy luận.

- **Tỷ lệ thành công**: 40% thành công nghiêm ngặt (2/5 test case), 60% thành công một phần (3/5) theo file `phase4_agent_v2_eval_20260406_154221.json`.
- **Kết quả chính**: So với chatbot baseline, agent cho câu trả lời bám tool tốt hơn, có nguồn tham chiếu và có bước trung gian rõ ràng cho bài toán giá/thuế; trong khi baseline chủ yếu trả lời chung chung hoặc khó kiểm chứng ở tác vụ nhiều bước.

---

## 2. Kiến Trúc Hệ Thống & Công Cụ

### 2.1 Cách triển khai vòng lặp ReAct
Luồng xử lý trong `ReActAgent` gồm:
1. Tạo prompt từ lịch sử hội thoại và system policy.
2. LLM trả về một trong hai dạng:
   - `Action: tool_name(arguments)`, hoặc
   - `Final Answer: ...`
3. Agent parse action, thực thi một tool, rồi thêm `Observation` vào history.
4. Lặp lại cho đến khi có đáp án cuối hoặc chạm `max_steps`.
5. Mỗi bước đều được log (`AGENT_STEP`, `TOOL_CALL`, `LLM_METRIC`, `AGENT_END`) để truy vết.

`ReActAgentV2` bổ sung guardrail theo domain (chỉ e-commerce), ràng buộc chặt hơn khi gọi tool, và recovery hint khi chạm giới hạn bước.

### 2.2 Danh mục công cụ (Inventory)
| Tên Tool | Định dạng Input | Mục đích sử dụng |
| :--- | :--- | :--- |
| `price_lookup` | `string` (tên sản phẩm) | Lấy/parse giá sản phẩm từ URL cửa hàng đã map, có fallback demo data. |
| `check_stock` | `string` (tên sản phẩm) | Suy luận trạng thái còn hàng/hết hàng từ trang cửa hàng, có fallback demo data. |
| `get_discount` | `string` (mã giảm giá) | Tìm snippet trên web để lấy phần trăm giảm giá và tổng hợp mức tốt nhất. |
| `calc_shipping` | `string` (`"<weight_kg>, <destination>"`) | Tính phí vận chuyển qua GHN API (hoặc fallback demo khi thiếu env). |
| `calculator` | `string` (biểu thức toán) | Tính toán số học cho tổng tiền, VAT và giá cuối cùng. |
| `web_search` | `string` (truy vấn) | Tìm kiếm web qua DuckDuckGo và trả về tiêu đề/mô tả/link kết quả. |

### 2.3 LLM Providers sử dụng
- **Chính**: OpenAI `gpt-4o` (theo `DEFAULT_PROVIDER=openai` và các run log).
- **Dự phòng**: Gemini `gemini-1.5-flash` (được hỗ trợ trong provider factory), thêm tùy chọn local GGUF (`Phi-3-mini-4k-instruct`).

---

## 3. Telemetry & Dashboard Hiệu Năng

Số liệu được tổng hợp từ log theo từng câu hỏi tại `logs/questions/20260406_154221_question_*.log` (sự kiện `LLM_METRIC`, tổng 27 lần gọi LLM):

- **Độ trễ trung vị (P50)**: `1055 ms`
- **Độ trễ cao (P99)**: `2446 ms` (nearest-rank p99 trên 27 mẫu)
- **Số token trung bình mỗi tác vụ**: `889.15` token mỗi lần gọi LLM
- **Tổng chi phí test suite**: `$0.24007` (theo công thức mock của dự án: `total_tokens/1000 * 0.01`)

Tín hiệu vận hành từ cùng run:
- 5 câu hỏi được xử lý, 23 lần gọi tool, 1 lỗi parser, 2 lần recovery khi chạm `max_steps` (`V2_RECOVERY_HINT`).

---

## 4. Phân Tích Nguyên Nhân Gốc (RCA) - Vết Lỗi

### Case Study: Thiếu coverage tool + lỗi parse fallback (Case 04)
- **Input**: So sánh Nintendo Switch đa thị trường, quy đổi ngoại tệ + thuế nhập khẩu + VAT.
- **Quan sát**:
  - Lần gọi tool sớm trả về lỗi: `Error: no live URL mapping configured for 'nintendo switch oled'. Supported products: iphone 15, macbook air m3.`
  - Ở step 7, model tạo text dạng kế hoạch tự do thay vì `Action:`/`Final Answer`, gây `PARSER_ERROR`.
  - Phiên chạy kết thúc do chạm `max_steps`.
- **Nguyên nhân gốc**:
  1. Inventory tool map theo sản phẩm còn hẹp (chỉ một vài sản phẩm có URL live).
  2. Prompt ràng buộc chặt nhưng chưa có chiến lược fallback đủ mạnh khi các tool liên tục trả lỗi unsupported.
  3. Parser phụ thuộc format đầu ra tuyệt đối; khi model drift sang narrative thì vòng lặp mất trạng thái.

### Case Study: Bài toán bundle vượt quá độ chi tiết của tool hiện tại (Case 05)
- **Input**: 12 bàn phím + 12 chuột, kiểm tra tồn kho đa cửa hàng, áp dụng giảm giá số lượng, tối ưu phí ship.
- **Quan sát**:
  - Nhiều lần gọi tool thất bại do tên sản phẩm không được hỗ trợ (`mechanical keyboard`, `... store mechanical keyboard`).
  - Agent tiếp tục lặp nhưng không hội tụ được kế hoạch hợp lệ trước `max_steps`.
- **Nguyên nhân gốc**:
  1. Chưa có tool chuyên cho tối ưu giỏ hàng/chia đơn.
  2. Chuẩn hóa tên sản phẩm còn yếu (tool kỳ vọng key map chính xác).
  3. `max_steps=8` chưa đủ cho bài toán nhiều ràng buộc nếu không có planner chuyên dụng.

---

## 5. Thí Nghiệm Ablation & So Sánh

### Thí nghiệm 1: Prompt v1 vs Prompt v2
- **Khác biệt**:
  - Prompt v2 bổ sung policy chặt: giới hạn domain e-commerce, mỗi bước chỉ 1 tool, retry khi lỗi, query web ngắn, và format final-answer rõ ràng.
  - Agent v2 bổ sung chặn ngoài domain và logging recovery hint.
- **Kết quả**:
  - Độ tin cậy tăng ở các case có coverage tool (ví dụ Case 01 có link nguồn và phép tính thuế tái kiểm chứng được).
  - Đánh đổi: case ngoài coverage chuyển sang fail rõ ràng (max-step) thay vì trả lời suy đoán dài dòng.

### Thí nghiệm 2 (Bonus): Chatbot vs Agent
| Trường hợp | Kết quả Chatbot | Kết quả Agent | Bên tốt hơn |
| :--- | :--- | :--- | :--- |
| Case 01 (giá + thuế) | Từ chối dữ liệu thời gian thực, không tính kết quả cuối từ dữ liệu live | Trả về cửa hàng rẻ nhất, có link và có tính thuế | **Agent** |
| Case 02 (ship + discount) | Yêu cầu người dùng cung cấp thêm dữ liệu | Cho kết quả end-to-end (có một phần giả định) | **Agent** |
| Case 03 (stock + VAT) | Không xác minh được tồn kho | Có ước tính dựa trên tool và nêu giả định | **Agent** |
| Case 04 (FX import) | Chỉ hướng dẫn chung | Timeout do thiếu mapping sản phẩm + parser drift | Hòa |
| Case 05 (bundle plan) | Kế hoạch giả định, không xác minh | Timeout do thiếu mapping sản phẩm | Hòa |

---

## 6. Đánh Giá Sẵn Sàng Production

- **Bảo mật**:
  - Input tool đã được làm sạch một phần (ví dụ `calculator` giới hạn ký tự hợp lệ, shipping kiểm tra trọng lượng số).
  - Cần bổ sung: validation mạnh hơn và parse theo schema cho toàn bộ tool.
- **Guardrails**:
  - Hiện có: `max_steps`, format output nghiêm ngặt, chặn domain, telemetry cho parser/tool failures.
  - Cần bổ sung: ngưỡng confidence và chính sách fail-fast khi gặp lỗi unsupported lặp lại.
- **Khả năng mở rộng**:
  - Kiến trúc hiện tại là ReAct loop tuyến tính + đăng ký tool động qua registry.
  - Hướng nâng cấp: tách planner-executor (hoặc orchestration dạng graph) cho bài toán nhiều ràng buộc, đồng thời mở rộng canonicalization cho sản phẩm.

---
