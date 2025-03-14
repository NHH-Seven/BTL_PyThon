from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QHBoxLayout, QGraphicsDropShadowEffect)
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer
from database_connection import connect_db
import hashlib
import sys
import globals

class LoginForm(QWidget):
    def __init__(self, onLoginSuccess=None):
        super().__init__()
        self.onLoginSuccess = onLoginSuccess
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Đăng Nhập - Quản Lý Quán Café")
        self.setFixedSize(900, 600)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left side - Image background
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                background-color: #5D4037;
                border-radius: 10px 0px 0px 10px;
            }
        """)
        image_layout = QVBoxLayout(image_frame)
        
        # Add coffee shop logo
        logo_label = QLabel("☕")
        logo_label.setFont(QFont("Arial", 80))
        logo_label.setStyleSheet("color: white;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Welcome text
        welcome_text = QLabel("Chào mừng đến với\nQuản Lý Quán Café")
        welcome_text.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        welcome_text.setStyleSheet("color: white;")
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Motto text
        motto_text = QLabel("Nơi mỗi giọt cà phê được quản lý chuyên nghiệp")
        motto_text.setFont(QFont("Arial", 14))
        motto_text.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        motto_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        image_layout.addStretch()
        image_layout.addWidget(logo_label)
        image_layout.addSpacing(20)
        image_layout.addWidget(welcome_text)
        image_layout.addWidget(motto_text)
        image_layout.addStretch()
        
        main_layout.addWidget(image_frame, 1)
        
        # Right side - Login form
        login_frame = QFrame()
        login_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 0px 10px 10px 0px;
            }
        """)
        
        # Add simple shadow to the login form
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(-2, 0)
        login_frame.setGraphicsEffect(shadow)
        
        login_layout = QVBoxLayout(login_frame)
        login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.setSpacing(20)
        login_layout.setContentsMargins(50, 50, 50, 50)
        
        # Login form content
        login_title = QLabel("Đăng Nhập")
        login_title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_title.setStyleSheet("color: #5D4037;")
        
        login_subtitle = QLabel("Vui lòng đăng nhập để tiếp tục")
        login_subtitle.setFont(QFont("Arial", 12))
        login_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_subtitle.setStyleSheet("color: #9E9E9E;")
        
        # Username input with icon
        username_container = QFrame()
        username_layout = QHBoxLayout(username_container)
        username_layout.setContentsMargins(0, 0, 0, 0)
        username_layout.setSpacing(10)
        
        username_icon = QLabel("👤")
        username_icon.setStyleSheet("font-size: 18px;")
        username_icon.setFixedWidth(30)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Tên đăng nhập")
        self.username.setMinimumHeight(45)
        
        username_layout.addWidget(username_icon)
        username_layout.addWidget(self.username)
        
        # Password input with icon
        password_container = QFrame()
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(10)
        
        password_icon = QLabel("🔒")
        password_icon.setStyleSheet("font-size: 18px;")
        password_icon.setFixedWidth(30)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Mật khẩu")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setMinimumHeight(45)
        
        password_layout.addWidget(password_icon)
        password_layout.addWidget(self.password)
        
        # Login button
        login_button = QPushButton("ĐĂNG NHẬP")
        login_button.setMinimumHeight(50)
        login_button.clicked.connect(self.login)
        
        # Register link
        self.register_window = None
        switch_to_register = QPushButton("Chưa có tài khoản? Đăng ký ngay")
        switch_to_register.setFlat(True)
        switch_to_register.clicked.connect(self.show_register)
        
        # Add widgets to login layout
        login_layout.addStretch()
        login_layout.addWidget(login_title)
        login_layout.addWidget(login_subtitle)
        login_layout.addSpacing(20)
        login_layout.addWidget(username_container)
        login_layout.addWidget(password_container)
        login_layout.addSpacing(20)
        login_layout.addWidget(login_button)
        login_layout.addWidget(switch_to_register, 0, Qt.AlignmentFlag.AlignCenter)
        login_layout.addStretch()
        
        main_layout.addWidget(login_frame, 1)
        
        # Apply styles
        self.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #5D4037;
            }
            QPushButton {
                background-color: #5D4037;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8D6E63;
            }
            QPushButton[flat=true] {
                background: none;
                border: none;
                color: #5D4037;
                font-weight: normal;
                text-decoration: underline;
            }
            QPushButton[flat=true]:hover {
                color: #8D6E63;
            }
        """)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self):
        username = self.username.text()
        password = self.hash_password(self.password.text())
        
        if not username or not self.password.text():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT id, name, role 
                    FROM users 
                    WHERE username = %s AND password = %s
                """, (username, password))
                user = cursor.fetchone()
                
                if user:
                    # Save current user ID to global variable
                    globals.current_user_id = user[0]
                    
                    # Call the onLoginSuccess callback
                    if self.onLoginSuccess:
                        self.onLoginSuccess()
                    self.hide()
                else:
                    QMessageBox.warning(self, "Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng!")
            finally:
                cursor.close()
                conn.close()
    
    def set_register_window(self, register_window):
        self.register_window = register_window
    
    def show_register(self):
        if self.register_window:
            self.register_window.show()
            self.hide()
        else:
            # Import here to avoid circular imports
            from form.register_form import RegisterWindow
            self.register_window = RegisterWindow()
            self.register_window.set_login_form(self)
            self.register_window.show()
            self.hide()
        
    def closeEvent(self, event):
        sys.exit()

# Standalone test for this module
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LoginForm()
    window.show()
    sys.exit(app.exec())