import json
import os
import streamlit as st
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import logging
from models.chroma_loader import load_existing_chroma_db
from models.rag_retriever_handler import generate_answer

# Thiết lập logging
logging.basicConfig(level=logging.INFO)


# Thiết lập trang Streamlit
def setup_page():
    st.set_page_config(
        page_title="StockAI - Chatbot",
        page_icon="🤖",
        layout="wide",
    )
    
# Cấu hình trang
setup_page()

# Tải cơ sở dữ liệu vector
def load_vectordb(db_path):
    vector_db = load_existing_chroma_db(db_path)
    print(f"Number of documents in vector DB: {len(vector_db.get())}")
    return vector_db

# Định dạng câu trả lời từ JSON
def format_output(json_output):
    answer = json_output["answer"]
    answer += "\n\nNguồn: "
    for title, link in zip(json_output["titles"], json_output["links"]):
        answer += f"\n\n[{title}]({link})"
    return answer

# Hàm xử lý câu hỏi và lưu vào lịch sử
def process_question(prompt, msgs, vector_db):
    msgs.add_user_message(prompt)

    # Gọi hàm generate_answer
    response = generate_answer(vector_db, prompt)
    print(f"Response received: {response}")

    if response:
        try:
            json_output = json.loads(response)
            answer_text = format_output(json_output)
            if answer_text:
                # Thêm câu trả lời vào lịch sử và hiển thị ngay lập tức
                msgs.add_ai_message(answer_text)
                st.chat_message("assistant").write(answer_text)
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Error processing response: {e}")
            st.error("Lỗi khi xử lý phản hồi từ hệ thống. Hãy thử lại sau.")



# Khởi tạo lịch sử trò chuyện
msgs = StreamlitChatMessageHistory(key="chat_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("Tôi là trợ lý ảo của bạn. Hãy hỏi tôi về chứng khoán.")

# Tải cơ sở dữ liệu vector
vector_db = load_vectordb("vector_db")

# Thiết lập tiêu đề ứng dụng
st.title("StockAI - Tư vấn Chứng khoán")

# Tải file CSS với encoding UTF-8
with open("styles/Chatbot.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Hiển thị lịch sử trò chuyện hiện tại
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# Phần nhập câu hỏi
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    process_question(prompt, msgs, vector_db)

# Hiển thị các tin nhắn mới nhất ngay lập tức
with st.container():
    st.markdown("<div class='input-container'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
