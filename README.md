# Day 27: Hệ thống Agent Human-in-the-Loop (HITL)

Học Viên Hoàng Vũ Trung Nguyên - 2A202601076

Đây là Lab 27 xây dựng workflow LangGraph đánh giá churn risk của khách hàng có tích hợp Human-in-the-Loop qua Streamlit.

## 🚀 Cách cài đặt dependency
1. Yêu cầu Python 3.10+
2. Cài đặt các thư viện bằng pip:
```bash
pip install -r requirements.txt
```

## 🧠 Chạy hệ thống
Trong lab này, logic LLM được giả lập bằng code (mocked) ở node `evaluate_customer` bên trong file `graph.py`, do đó bạn **không cần** cần tạo API Key nào cả.

Bạn chỉ cần khởi chạy Streamlit UI để test toàn bộ LangGraph workflow:
```bash
streamlit run app.py
```

## 🔧 Cấu hình Policy & Rule
- **Confidence Threshold**: 0.85
- **Hard Policy**: 
  - Auto-Execute: `send_email` và confidence >= 0.85.
  - Escalate (Buộc Review): Tất cả các action dưới 0.85 confidence score.
  - Policy Override: Action `increase_credit_limit` luôn phải bị chặn và review cho dù confidence là 0.99.

## 🧑‍💻 Cách thức Review (Approve, Reject, Edit)
- Chọn Customer ID và bấm "Start Workflow" ở Sidebar để invoke Graph.
- Với trường hợp cần Review, Graph sẽ rơi vào trạng thái "Pending" và kích hoạt giao diện Streamlit HITL.
- Bạn có thể thao tác:
  - **Approve**: Phê duyệt action của agent, action gốc được chạy.
  - **Reject**: Từ chối, action bị abort (hủy bỏ).
  - **Edit & Submit**: Thay đổi nội dung action đề xuất (VD: đổi thành `decrease_credit_limit`) và chạy action đó.

## 📜 Audit Log
Mọi quyết định auto-execute từ hệ thống hay các phê duyệt từ human operator (Approve, Reject, Edit) đều được ghi nhận (append) trực tiếp vào file JSON `audit_log.json` lưu trong cùng thư mục root.
