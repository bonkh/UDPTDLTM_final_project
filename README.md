# Ứng dụng phân tích chỉ số chứng Khoán Vietstock
Ứng dụng phân tích dữ liệu thông minh


| Họ và tên                    | MSSV     | Github            |
| ---------------------------- | -------- | ----------------- |
| Nguyễn Văn Quang Hưng        | 21120247 | @HungLVT          |
| Huỳnh Cao Khôi               | 21120275 | @bonkh            |
| Hoàng Trung Nam              | 21120290 | @HTNam1710        |
| Chiêm Bỉnh Nguyên            | 21120294 | @DSGrid23         |
| Huỳnh Trí Nhân               | 21120302 | @HuynhTriNhan     |
| Nguyễn Đức Mạnh              | 20120019 | @manhhk15         |


## 1. Giới thiệu 
- Ứng dụng phân tích chỉ số chứng khoán Vietstock là ứng dụng giúp người dùng có thể phân tích dữ liệu chứng khoán một cách nhanh chóng và hiệu quả. Ứng dụng sử dụng dữ liệu từ trang web [Vietstock](https://finance.vietstock.vn/ket-qua-giao-dich?tab=thong-ke-gia).

### 1.1 Công nghệ sử dụng
- Airflow: Lập lịch thu thập các chỉ số chứng khoáng hằng ngày
- Streamlit: Hiển thị dữ liệu chứng khoán và phân tích dữ liệu
- Docker: Containerize ứng dụng
- RAG (Retrieval-Augmented Generation): Mô hình chatbot trả lời câu hỏi về dữ liệu chứng khoán

## 2. Cài đặt
### 2.1. Cài đặt môi trường Airflow 
- Đọc file hướng dẫn trong `dags/README.md`

### 2.2. Cài đặt môi trường Streamlit
- Đọc file hướng dẫn trong `Dashboard/README.md`