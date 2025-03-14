import mysql.connector

def connect_db():
    try:
        db = mysql.connector.connect(
            host="localhost",  # XAMPP chạy MySQL trên localhost
            user="root",       # Mặc định user trong XAMPP
            password="",       # Mật khẩu mặc định của MySQL trong XAMPP là rỗng
            database="db_db"    # Sử dụng database theo yêu cầu
        )
        return db
    except mysql.connector.Error as err:
        print(f"Lỗi kết nối CSDL: {err}")
        return None
