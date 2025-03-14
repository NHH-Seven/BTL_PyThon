from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel, 
                              QPushButton, QLineEdit, QMessageBox)
from PySide6.QtCore import Qt

from database_connection import connect_db

class UserProfileDialog(QDialog):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Thông Tin Cá Nhân")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px;
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton#cancelButton {
                background-color: #757575;
            }
            QPushButton#cancelButton:hover {
                background-color: #616161;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Hiển thị thông tin người dùng
        form_layout = QGridLayout()
        form_layout.setColumnStretch(1, 1)
        
        # ID (không thể chỉnh sửa)
        form_layout.addWidget(QLabel("ID:"), 0, 0)
        id_field = QLineEdit(self.user_data["id"])
        id_field.setReadOnly(True)
        id_field.setStyleSheet("background-color: #f0f0f0;")
        form_layout.addWidget(id_field, 0, 1)
        
        # Username (không thể chỉnh sửa)
        form_layout.addWidget(QLabel("Tên đăng nhập:"), 1, 0)
        username_field = QLineEdit(self.user_data.get("username", ""))
        username_field.setReadOnly(True)
        username_field.setStyleSheet("background-color: #f0f0f0;")
        form_layout.addWidget(username_field, 1, 1)
        
        # Họ tên
        form_layout.addWidget(QLabel("Họ tên:"), 2, 0)
        self.name_field = QLineEdit(self.user_data["name"])
        form_layout.addWidget(self.name_field, 2, 1)
        
        # Email
        form_layout.addWidget(QLabel("Email:"), 3, 0)
        self.email_field = QLineEdit(self.user_data["email"])
        form_layout.addWidget(self.email_field, 3, 1)
        
        # Số điện thoại
        form_layout.addWidget(QLabel("Số điện thoại:"), 4, 0)
        self.phone_field = QLineEdit(self.user_data["phone"])
        form_layout.addWidget(self.phone_field, 4, 1)
        
        # Vai trò (không thể chỉnh sửa)
        form_layout.addWidget(QLabel("Vai trò:"), 5, 0)
        role_field = QLineEdit(self.user_data["role"])
        role_field.setReadOnly(True)
        role_field.setStyleSheet("background-color: #f0f0f0;")
        form_layout.addWidget(role_field, 5, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QGridLayout()
        button_layout.setColumnStretch(0, 1)
        button_layout.setColumnStretch(1, 1)
        
        save_button = QPushButton("Lưu thay đổi")
        save_button.clicked.connect(self.saveChanges)
        button_layout.addWidget(save_button, 0, 0)
        
        cancel_button = QPushButton("Hủy")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button, 0, 1)
        
        layout.addLayout(button_layout)
    
    def saveChanges(self):
        # Kiểm tra thông tin nhập vào
        name = self.name_field.text().strip()
        email = self.email_field.text().strip()
        phone = self.phone_field.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập họ tên!")
            return
        
        if not email:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập email!")
            return
        
        # Cập nhật thông tin vào CSDL
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users
                    SET name = %s, email = %s, phone = %s
                    WHERE id = %s
                """, (name, email, phone, self.user_data["id"]))
                conn.commit()
                
                # Cập nhật lại dữ liệu người dùng
                self.user_data["name"] = name
                self.user_data["email"] = email
                self.user_data["phone"] = phone
                
                QMessageBox.information(self, "Thành công", "Thông tin đã được cập nhật!")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật thông tin: {str(e)}")
            finally:
                conn.close()
class ChangePasswordDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Đổi Mật Khẩu")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px;
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton#cancelButton {
                background-color: #757575;
            }
            QPushButton#cancelButton:hover {
                background-color: #616161;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        form_layout = QGridLayout()
        form_layout.setColumnStretch(1, 1)
        
        # Mật khẩu hiện tại
        form_layout.addWidget(QLabel("Mật khẩu hiện tại:"), 0, 0)
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.current_password, 0, 1)
        
        # Mật khẩu mới
        form_layout.addWidget(QLabel("Mật khẩu mới:"), 1, 0)
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.new_password, 1, 1)
        
        # Nhập lại mật khẩu mới
        form_layout.addWidget(QLabel("Nhập lại mật khẩu mới:"), 2, 0)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.confirm_password, 2, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QGridLayout()
        button_layout.setColumnStretch(0, 1)
        button_layout.setColumnStretch(1, 1)
        
        save_button = QPushButton("Đổi mật khẩu")
        save_button.clicked.connect(self.changePassword)
        button_layout.addWidget(save_button, 0, 0)
        
        cancel_button = QPushButton("Hủy")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button, 0, 1)
        
        layout.addLayout(button_layout)
    
    def changePassword(self):
        current_password = self.current_password.text()
        new_password = self.new_password.text()
        confirm_password = self.confirm_password.text()
        
        # Kiểm tra các trường đã nhập
        if not current_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu mới không khớp!")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu mới phải có ít nhất 6 ký tự!")
            return
        
        # Kiểm tra mật khẩu hiện tại
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT password FROM users 
                    WHERE id = %s
                """, (self.user_id,))
                
                result = cursor.fetchone()
                if not result:
                    QMessageBox.critical(self, "Lỗi", "Không tìm thấy thông tin người dùng!")
                    return
                
                stored_password = result[0]
                
                # Kiểm tra mật khẩu (trong thực tế cần hash password)
                if current_password != stored_password:
                    QMessageBox.warning(self, "Lỗi", "Mật khẩu hiện tại không đúng!")
                    return
                
                # Cập nhật mật khẩu mới
                cursor.execute("""
                    UPDATE users 
                    SET password = %s 
                    WHERE id = %s
                """, (new_password, self.user_id))
                
                conn.commit()
                QMessageBox.information(self, "Thành công", "Mật khẩu đã được cập nhật!")
                self.accept()
                
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật mật khẩu: {str(e)}")
            finally:
                conn.close()