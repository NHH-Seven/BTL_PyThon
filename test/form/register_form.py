import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QHBoxLayout, QGridLayout, QSpacerItem)
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor
from PySide6.QtCore import Qt, QSize, Signal, Slot
from database_connection import connect_db
import hashlib
import re

class ValidatingLineEdit(QLineEdit):
    """Custom QLineEdit that validates input"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(45)
        self.is_valid = False
        self.error_message = ""
        
        # Style for valid and invalid states
        self.valid_style = """
            background-color: #F5F5F5;
            border: 1px solid #E0E0E0;
        """
        
        self.invalid_style = """
            background-color: #FFF8F8;
            border: 1px solid #FFCCCC;
        """
        
        self.textChanged.connect(self.validate)
        self.setStyleSheet(self.valid_style)
        
    def set_validation_function(self, validator_func, error_msg):
        """Set the validation function and error message"""
        self.validator_func = validator_func
        self.default_error_msg = error_msg
        
    def validate(self):
        """Run validation and update appearance"""
        text = self.text()
        
        if hasattr(self, 'validator_func'):
            if text:
                valid, message = self.validator_func(text)
                self.is_valid = valid
                self.error_message = message if message else self.default_error_msg
            else:
                # Empty field - not valid but don't show error yet
                self.is_valid = False
                self.error_message = ""
                self.setStyleSheet(self.valid_style)
                return
        else:
            # If no validator is set, consider valid
            self.is_valid = True
            self.error_message = ""
            
        if self.is_valid:
            self.setStyleSheet(self.valid_style)
            self.setToolTip("")
        else:
            self.setStyleSheet(self.invalid_style)
            self.setToolTip(self.error_message)

class RegisterWindow(QWidget):
    def __init__(self, login_form=None):
        super().__init__()
        self.login_form = login_form
        self.setup_database()
        self.initUI()
    
    def setup_database(self):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(10) PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL,
                        phone VARCHAR(15),
                        role VARCHAR(20) DEFAULT 'Nhân viên'
                    )
                """)
                conn.commit()
            except Exception as e:
                print(f"Lỗi khi tạo bảng: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def initUI(self):
        self.setWindowTitle("Đăng Ký - Cafe Manager")
        self.setFixedSize(1000, 650)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left side - Image with coffee theme
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                background-color: #5D4037;
                border-radius: 0px;
            }
        """)
        image_layout = QVBoxLayout(image_frame)
        image_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.setContentsMargins(30, 50, 30, 50)
        
        # Logo and welcome text
        logo_label = QLabel("☕")
        logo_label.setFont(QFont("Arial", 80))
        logo_label.setStyleSheet("color: #FFCC80;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        cafe_name = QLabel("COFFEE HOUSE")
        cafe_name.setFont(QFont("Trebuchet MS", 30, QFont.Weight.Bold))
        cafe_name.setStyleSheet("color: #FFCC80; margin-top: -20px;")
        cafe_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        slogan = QLabel("Quản lý dễ dàng - Kinh doanh hiệu quả")
        slogan.setFont(QFont("Arial", 14))
        slogan.setStyleSheet("color: #E6E6E6; margin-top: 10px;")
        slogan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        features_container = QFrame()
        features_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin-top: 40px;
            }
        """)
        features_layout = QVBoxLayout(features_container)
        
        features_title = QLabel("Tính năng nổi bật")
        features_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        features_title.setStyleSheet("color: #FFCC80;")
        features_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        features = [
            
            "✓ Theo dõi doanh thu theo thời gian thực",
            "✓ Quản lý sản phẩm, nhân viên",
            "✓ Phân quyền nhân viên chi tiết",
            "✓ Báo cáo thống kê trực quan"
        ]
        
        features_layout.addWidget(features_title)
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setFont(QFont("Arial", 12))
            feature_label.setStyleSheet("color: white; margin: 5px 0;")
            features_layout.addWidget(feature_label)
        
        image_layout.addWidget(logo_label)
        image_layout.addWidget(cafe_name)
        image_layout.addWidget(slogan)
        image_layout.addWidget(features_container)
        
        # Right side - Register form
        register_frame = QFrame()
        register_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 0px;
            }
        """)
        register_layout = QVBoxLayout(register_frame)
        register_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        register_layout.setSpacing(20)
        register_layout.setContentsMargins(50, 50, 50, 50)
        
        # Register form content
        register_title = QLabel("Đăng Ký Tài Khoản")
        register_title.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        register_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        register_title.setStyleSheet("color: #5D4037; margin-bottom: 10px;")
        
        register_subtitle = QLabel("Điền thông tin để tạo tài khoản mới")
        register_subtitle.setFont(QFont("Arial", 12))
        register_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        register_subtitle.setStyleSheet("color: #757575; margin-bottom: 20px;")
        
        # Form grid layout
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(15)
        
        # Input fields with icons and validation
        self.create_input_field(form_layout, 0, 0, "👤", "Tên đăng nhập", "username", 
                               self.validate_username)
        
        self.create_input_field(form_layout, 1, 0, "🔒", "Mật khẩu", "password", 
                               self.validate_password, is_password=True)
        
        self.create_input_field(form_layout, 2, 0, "🔒", "Xác nhận mật khẩu", "confirm", 
                               self.validate_confirm_password, is_password=True)
        
        self.create_input_field(form_layout, 0, 1, "📝", "Họ và tên", "name", 
                               self.validate_name)
        
        self.create_input_field(form_layout, 1, 1, "📧", "Email", "email", 
                               self.validate_email)
        
        self.create_input_field(form_layout, 2, 1, "📱", "Số điện thoại", "phone", 
                               self.validate_phone)
        
        # Error message area
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #D32F2F; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        
        # Register button
        self.register_button = QPushButton("ĐĂNG KÝ")
        self.register_button.setMinimumHeight(50)
        self.register_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.register_button.clicked.connect(self.register)
        self.register_button.setEnabled(False)  # Initially disabled
        
        # Login link
        login_container = QFrame()
        login_layout = QHBoxLayout(login_container)
        login_layout.setContentsMargins(0, 0, 0, 0)
        
        login_text = QLabel("Đã có tài khoản?")
        login_text.setFont(QFont("Arial", 12))
        login_text.setStyleSheet("color: #757575;")
        
        switch_to_login = QPushButton("Đăng nhập ngay")
        switch_to_login.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        switch_to_login.clicked.connect(self.show_login)
        switch_to_login.setFlat(True)
        switch_to_login.setCursor(Qt.CursorShape.PointingHandCursor)
        
        login_layout.addWidget(login_text)
        login_layout.addWidget(switch_to_login)
        login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add widgets to register layout
        register_layout.addWidget(register_title)
        register_layout.addWidget(register_subtitle)
        register_layout.addLayout(form_layout)
        register_layout.addWidget(self.error_label)
        register_layout.addItem(QSpacerItem(20, 10))
        register_layout.addWidget(self.register_button)
        register_layout.addWidget(login_container)
        register_layout.addStretch()
        
        # Add main panels to layout
        main_layout.addWidget(image_frame, 4)
        main_layout.addWidget(register_frame, 6)
        
        # Apply global styles
        self.setStyleSheet("""
            QLineEdit {
                padding: 12px 12px 12px 40px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                background-color: #F5F5F5;
            }
            QLineEdit:focus {
                border: 2px solid #5D4037;
                background-color: white;
            }
            QPushButton {
                background-color: #5D4037;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4E342E;
            }
            QPushButton:disabled {
                background-color: #BCAAA4;
                color: #F5F5F5;
            }
            QPushButton[flat=true] {
                background: none;
                border: none;
                color: #5D4037;
                font-weight: bold;
                padding: 0px;
                text-decoration: none;
            }
            QPushButton[flat=true]:hover {
                color: #8D6E63;
                text-decoration: underline;
            }
            QLabel[iconLabel=true] {
                color: #757575;
                font-size: 16px;
                padding-left: 12px;
            }
        """)
        
        # Connect text changed signals to check form validity
        for field_name in ["username", "password", "confirm", "name", "email", "phone"]:
            field = getattr(self, field_name)
            field.textChanged.connect(self.check_form_validity)
    
    def create_input_field(self, layout, row, col, icon, placeholder, attribute_name, 
                          validator_func=None, is_password=False, error_msg=""):
        field_container = QFrame()
        field_layout = QHBoxLayout(field_container)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(0)
        
        # Icon label
        icon_label = QLabel(icon)
        icon_label.setProperty("iconLabel", True)
        icon_label.setStyleSheet("""
            QLabel {
                color: #757575;
                font-size: 16px;
                background-color: transparent;
                padding: 0 5px;
                margin-left: 10px;
                z-index: 2;
                position: absolute;
            }
        """)
        
        # Input field with validation
        input_field = ValidatingLineEdit(placeholder)
        
        if is_password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
        
        if validator_func:
            if attribute_name == "confirm":
                # Special case for password confirmation
                error_msg = "Mật khẩu xác nhận không khớp!"
            elif attribute_name == "password":
                error_msg = "Mật khẩu phải có ít nhất 6 ký tự!"
            elif attribute_name == "email":
                error_msg = "Email không hợp lệ!"
            elif attribute_name == "phone":
                error_msg = "Số điện thoại không hợp lệ!"
            elif attribute_name == "username":
                error_msg = "Không được để trống ô dữ liệu nào cả!"
            elif attribute_name == "name":
                error_msg = "Họ tên không được để trống!"
                
            input_field.set_validation_function(validator_func, error_msg)
        
        # Store reference to field
        setattr(self, attribute_name, input_field)
        
        # Add feedback icon (will be shown on validation)
        feedback_label = QLabel("")
        feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feedback_label.setFixedSize(30, 30)
        setattr(self, f"{attribute_name}_feedback", feedback_label)
        
        # Add to layout
        field_layout.addWidget(icon_label)
        field_layout.addWidget(input_field)
        field_layout.addWidget(feedback_label)
        
        layout.addWidget(field_container, row, col)
    
    def validate_username(self, text):
        """Validate username and check database for duplicates"""
        if not text.strip():
            return False, "Tên đăng nhập không được để trống!"
        
        # Check for username in database (only do this if username is not empty)
        if text.strip():
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT username FROM users WHERE username = %s", (text,))
                    if cursor.fetchone():
                        return False, "Tên đăng nhập đã tồn tại!"
                except Exception as e:
                    print(f"Error checking username: {str(e)}")
                finally:
                    cursor.close()
                    conn.close()
        
        return True, ""
    
    def validate_password(self, text):
        """Validate password"""
        if len(text) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự!"
        return True, ""
    
    def validate_confirm_password(self, text):
        """Validate password confirmation"""
        if not hasattr(self, 'password'):
            return False, "Vui lòng nhập mật khẩu trước!"
        
        if text != self.password.text():
            return False, "Mật khẩu xác nhận không khớp!"
        return True, ""
    
    def validate_name(self, text):
        """Validate full name"""
        if not text.strip():
            return False, "Họ tên không được để trống!"
        return True, ""
    
    def validate_email(self, text):
        """Validate email format and check for duplicates"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, text):
            return False, "Email không hợp lệ!"
        
        # Check for email in database
        if text.strip():
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT email FROM users WHERE email = %s", (text,))
                    if cursor.fetchone():
                        return False, "Email đã được sử dụng!"
                except Exception as e:
                    print(f"Error checking email: {str(e)}")
                finally:
                    cursor.close()
                    conn.close()
        
        return True, ""
    
    def validate_phone(self, text):
        """Validate phone number format"""
        pattern = r'^(0|\+84)\d{9,10}$'
        if not re.match(pattern, text):
            return False, "Số điện thoại không hợp lệ! Bắt đầu bằng 0 hoặc +84 và có 10-11 số."
        return True, ""
    
    def check_form_validity(self):
        """Check the validity of all fields and update the register button state"""
        # Check if all fields are filled and valid
        all_fields_filled = all([
            self.username.text().strip(),
            self.password.text(),
            self.confirm.text(),
            self.name.text().strip(),
            self.email.text().strip(),
            self.phone.text().strip()
        ])
        
        all_fields_valid = all([
            getattr(self, field).is_valid
            for field in ["username", "password", "confirm", "name", "email", "phone"]
            if hasattr(getattr(self, field), 'is_valid')
        ])
        
        # Update error message if any field is invalid
        error_msgs = []
        for field_name in ["username", "password", "confirm", "name", "email", "phone"]:
            field = getattr(self, field_name)
            if hasattr(field, 'error_message') and field.error_message:
                error_msgs.append(field.error_message)
        
        if error_msgs:
            self.error_label.setText(error_msgs[0])
        else:
            self.error_label.setText("")
        
        # Enable/disable register button
        self.register_button.setEnabled(all_fields_filled and all_fields_valid)
    
    def set_login_form(self, login_form):
        self.login_form = login_form
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_user_id(self, cursor):
        try:
            cursor.execute("SELECT id FROM users WHERE id LIKE 'NV%' ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
        
            if result and result[0]:
                last_id = result[0]
                last_number = int(last_id[2:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            new_id = f"NV{new_number:03d}"
            return new_id
        
        except Exception as e:
            print(f"Lỗi khi tạo mã nhân viên: {str(e)}")
            import random
            return f"NV{random.randint(1, 999):03d}"
    
    def register(self):
        # All validation is already done during typing, so we can directly proceed
        username = self.username.text().strip()
        password = self.password.text()
        name = self.name.text().strip()
        email = self.email.text().strip()
        phone = self.phone.text().strip()
        
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                # Final check for username and email duplicates (in case of race conditions)
                cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    self.show_error_message("Tên đăng nhập đã tồn tại!")
                    return
                
                cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    self.show_error_message("Email đã được sử dụng!")
                    return
                
                # Generate user ID and register
                user_id = self.generate_user_id(cursor)
                hashed_password = self.hash_password(password)
                
                cursor.execute("""
                    INSERT INTO users (id, username, password, name, email, phone, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, username, hashed_password, name, email, phone, 'Nhân viên'))
                conn.commit()
                
                self.show_success_message(
                    f"Đăng ký thành công!\n\nMã nhân viên của bạn: {user_id}\n\nVui lòng đăng nhập để tiếp tục."
                )
                
                # Clear form
                for widget in [self.username, self.password, self.confirm, 
                             self.name, self.email, self.phone]:
                    widget.clear()
                
                # Show login form
                self.show_login()
                    
            except Exception as e:
                print(f"Lỗi đăng ký: {str(e)}")
                self.show_error_message(
                    "Có lỗi xảy ra trong quá trình đăng ký!\nVui lòng thử lại sau."
                )
            finally:
                cursor.close()
                conn.close()
    
    def show_error_message(self, message):
        error_box = QMessageBox(self)
        error_box.setWindowTitle("Lỗi")
        error_box.setText(message)
        error_box.setIcon(QMessageBox.Icon.Warning)
        error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #5D4037;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 80px;
                min-height: 30px;
            }
        """)
        error_box.exec()
    
    def show_success_message(self, message):
        success_box = QMessageBox(self)
        success_box.setWindowTitle("Thành công")
        success_box.setText(message)
        success_box.setIcon(QMessageBox.Icon.Information)
        success_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        success_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                font-size: 14px;
            }
            QLabel {
                min-width: 300px;
            }
            QPushButton {
                background-color: #5D4037;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 80px;
                min-height: 30px;
            }
        """)
        success_box.exec()
    
    def show_login(self):
        if self.login_form:
            self.login_form.show()
            self.hide()
        else:
            # Import here to avoid circular imports
            from form.login_form import LoginForm
            self.login_form = LoginForm()
            self.login_form.set_register_window(self)
            self.login_form.show()
            self.hide()

# Standalone test for this module
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    # Make sure database_connection.py is in path
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec())