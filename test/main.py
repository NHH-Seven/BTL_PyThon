import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QStackedWidget, QHBoxLayout, QPushButton, QButtonGroup, QLabel, QFrame,
    QMessageBox, QMenu, QDialog, QSplitter)
from PySide6.QtGui import QFont, QCursor, QIcon, QPixmap
from PySide6.QtCore import Qt, QSize

from database_connection import connect_db


from form.user_dialogs import UserProfileDialog, ChangePasswordDialog
from form.login_form import LoginForm

import globals

from tabs.dashboard_tab import DashboardTab
from tabs.sales import SalesTab
from tabs.product_management import ProductManagementTab
from tabs.employee_management import EmployeeManagementTab
from tabs.order_management import OrderManagementTab
from tabs.statisticss import StatisticsTab
from tabs.cart import CartTab

class CafeManagementUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản Lý Quán Café")
        self.setMinimumSize(1400, 900)
        
        # Khởi chạy form đăng nhập trước
        self.showLoginForm()
    
    def showLoginForm(self):
        self.login_form = LoginForm(onLoginSuccess=self.initializeMainUI)
        self.login_form.show()
    
    def initializeMainUI(self):
        try:
            # Lấy thông tin người dùng hiện tại từ CSDL
            print(f"Initializing UI with user_id: {globals.current_user_id}")
            self.current_user = self.getUserInfo()
            if not self.current_user:
                print("Failed to get user info")
                return
        
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
        
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(0)
            main_layout.setContentsMargins(0, 0, 0, 0)
        
            self.createHeader(main_layout)
            self.createContent(main_layout)
            self.applyStyles()
        
            # Hiển thị cửa sổ chính
            self.show()
            
            print("Main UI initialized and shown")
        except Exception as e:
            print(f"Error initializing main UI: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def createHeader(self, layout):
        # Main header container
        header_container = QFrame()
        header_container.setObjectName("headerContainer")
        header_container.setFixedHeight(120)
        
        header_layout = QVBoxLayout(header_container)
        header_layout.setSpacing(0)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top bar with logo and user info
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(70)
        
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo section with icon and text
        logo_container = QFrame()
        logo_container.setObjectName("logoContainer")
        logo_layout = QHBoxLayout(logo_container)
        
        logo_icon = QLabel()
        logo_icon.setObjectName("logoIcon")
        # Placeholder for coffee icon (you could replace with an actual icon)
        logo_icon.setText("☕")
        logo_icon.setFont(QFont("Arial", 24))
        
        logo_text = QLabel("COFFEE MANAGEMENT")
        logo_text.setObjectName("logoText")
        logo_text.setFont(QFont("Montserrat", 18, QFont.Weight.Bold))
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        top_bar_layout.addWidget(logo_container)
        
        # Right side buttons
        right_buttons = QFrame()
        right_buttons.setObjectName("rightButtons")
        right_layout = QHBoxLayout(right_buttons)
        right_layout.setSpacing(15)
        
        # Cart button with counter
        self.cart_button = QPushButton()
        self.cart_button.setObjectName("cartButton")
        self.cart_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cart_button.setText("🛒 Giỏ hàng")
        self.cart_button.setFont(QFont("Roboto", 11))
        self.cart_button.clicked.connect(self.openCart)
        
        # User profile button
        self.user_button = QPushButton()
        self.user_button.setObjectName("userButton")
        self.user_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.user_button.setText(f"👤 {self.current_user['name']} ({self.current_user['role']})")
        self.user_button.setFont(QFont("Roboto", 11))
        self.user_button.clicked.connect(self.showUserMenu)
        
        right_layout.addWidget(self.cart_button)
        right_layout.addWidget(self.user_button)
        top_bar_layout.addWidget(right_buttons, alignment=Qt.AlignmentFlag.AlignRight)
        
        header_layout.addWidget(top_bar)
        
        # Navigation bar
        nav_bar = QFrame()
        nav_bar.setObjectName("navBar")
        nav_bar.setFixedHeight(50)
        
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(20, 0, 20, 0)
        nav_layout.setSpacing(5)
        
        self.nav_buttons = []
        nav_items = [
            ("🏠 Trang Chủ", 0, "dashboard"),
            ("🛒 Đặt Hàng", 1, "sales"),
            ("📋 Quản Lý Sản Phẩm", 2, "products"),
            ("👤 Quản Lý Nhân Viên", 3, "employees"),
            ("📦 Quản Lý Đơn Hàng", 4, "orders"),
            ("📊 Thống Kê", 5, "statistics")
        ]
        
        button_group = QButtonGroup(self)
        button_group.setExclusive(True)
        
        for text, index, obj_name in nav_items:
            btn = QPushButton(text)
            btn.setObjectName(f"navBtn{obj_name}")
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFont(QFont("Roboto", 11))
            btn.clicked.connect(lambda checked, x=index, t=text: self.handleTabChange(x, t))
            button_group.addButton(btn)
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        self.nav_buttons[0].setChecked(True)
        
        header_layout.addWidget(nav_bar)
        
        # Add a separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("headerSeparator")
        header_layout.addWidget(separator)
        
        layout.addWidget(header_container)

    def handleTabChange(self, index, tab_title):
        # Kiểm tra quyền truy cập cho các tab đặc biệt
        if index == 2:  # Quản Lý Sản Phẩm
            if self.current_user["role"].lower() != "admin":
                QMessageBox.warning(
                    self, 
                    "Quyền truy cập bị từ chối", 
                    "Chỉ Admin mới có quyền truy cập vào phần Quản Lý Sản Phẩm.",
                    QMessageBox.StandardButton.Ok
                )
                # Đặt lại nút đã chọn trước đó
                current_index = self.content_stack.currentIndex()
                if current_index < len(self.nav_buttons):
                    self.nav_buttons[current_index].setChecked(True)
                return
        
        elif index == 3:  # Quản Lý Nhân Viên
            if self.current_user["role"].lower() != "admin":
                QMessageBox.warning(
                    self, 
                    "Quyền truy cập bị từ chối", 
                    "Chỉ Admin mới có quyền truy cập vào phần Quản Lý Nhân Viên.",
                    QMessageBox.StandardButton.Ok
                )
                # Đặt lại nút đã chọn trước đó
                current_index = self.content_stack.currentIndex()
                if current_index < len(self.nav_buttons):
                    self.nav_buttons[current_index].setChecked(True)
                return
        
        # Nếu không có vấn đề quyền hạn, chuyển đến tab tương ứng
        self.content_stack.setCurrentIndex(index)

    def showUserMenu(self):
        menu = QMenu(self)
        menu.setObjectName("userMenu")
        
        profile_action = menu.addAction("👤 Thông tin cá nhân")
        change_password_action = menu.addAction("🔑 Đổi mật khẩu")
        menu.addSeparator()
        logout_action = menu.addAction("🚪 Đăng xuất")
    
        profile_action.triggered.connect(self.showProfile)
        change_password_action.triggered.connect(self.showChangePassword)
        logout_action.triggered.connect(self.logout)
    
        menu.exec_(QCursor.pos())

    def openCart(self):
        # Chuyển đến tab giỏ hàng
        self.content_stack.setCurrentIndex(self.cart_tab_index)
    
        # Bỏ chọn tất cả các nút điều hướng
        for button in self.nav_buttons:
            button.setChecked(False)

    def createContent(self, layout):
        # Content container
        content_container = QFrame()
        content_container.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create the stacked widget for different tabs
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        
        # Khởi tạo CartTab trước
        self.cart_tab = CartTab()
        
        # Main tabs with improved layouts
        self.tabs = [
            DashboardTab(),
            SalesTab(),
            ProductManagementTab(),
            EmployeeManagementTab(),
            OrderManagementTab(),
            StatisticsTab()
        ]
        
        # Set CartTab cho SalesTab
        self.tabs[1].setCartTab(self.cart_tab)
        
        # Thêm các tab vào stack
        for tab in self.tabs:
            self.content_stack.addWidget(tab)
        
        # Thêm CartTab vào cuối
        self.content_stack.addWidget(self.cart_tab)
        self.cart_tab_index = self.content_stack.count() - 1
        
        content_layout.addWidget(self.content_stack)
        layout.addWidget(content_container)

    def getUserInfo(self):
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                # Lấy user_id từ biến toàn cục đã lưu khi đăng nhập
                user_id = globals.current_user_id
            
                cursor.execute("""
                SELECT id, username, name, email, phone, role
                FROM users
                WHERE id = %s
                """, (user_id,))
                user = cursor.fetchone()
                if user:
                    return {
                        "id": user[0],
                        "username": user[1],
                        "name": user[2],
                        "email": user[3],
                        "phone": user[4],
                        "role": user[5]
                    }
            except Exception as e:
                print(f"Error fetching user info: {str(e)}")
            finally:
                conn.close()

        # Return default user info if database connection fails
        return {
            "id": "Unknown",
            "username": "unknown",
            "name": "Unknown User",
            "role": "User",
            "email": "unknown@example.com",
            "phone": "N/A"
        }

    def showProfile(self):
        dialog = UserProfileDialog(self.current_user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh user info
            self.current_user = self.getUserInfo()
            self.user_button.setText(f"👤 {self.current_user['name']} ({self.current_user['role']})")

    def showChangePassword(self):
        dialog = ChangePasswordDialog(self.current_user["id"], self)
        dialog.exec()

    def logout(self):
        reply = QMessageBox.question(
            self, 
            'Xác nhận', 
            'Bạn có chắc chắn muốn đăng xuất?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
    
        if reply == QMessageBox.StandardButton.Yes:
            # Xóa thông tin người dùng hiện tại
            globals.current_user_id = None
        
            # Đóng cửa sổ hiện tại và hiển thị form đăng nhập
            self.hide()
            self.showLoginForm()
    
    def showLoginForm(self):
        self.login_form = LoginForm(onLoginSuccess=lambda: print("Login successful") or self.initializeMainUI())
        self.login_form.show()
    
    def applyStyles(self):
        # Coffee theme styling for the entire application
        self.setStyleSheet("""
            QWidget {
                font-family: 'Roboto', 'Segoe UI', 'Arial', sans-serif;
                font-size: 12px;
                color: #3e2723;
            }
            
            #headerContainer {
                background-color: #4e342e;
                border-bottom: 1px solid #3e2723;
            }
            
            #topBar {
                background-color: #3e2723;
                color: #d7ccc8;
            }
            
            #logoContainer {
                padding: 5px;
            }
            
            #logoIcon {
                color: #ffcc80;
                font-size: 24px;
                padding-right: 10px;
            }
            
            #logoText {
                color: #d7ccc8;
                font-weight: bold;
            }
            
            #navBar {
                background-color: #5d4037;
                border-top: 1px solid #6d4c41;
            }
            
            #navBar QPushButton {
                color: #d7ccc8;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
                font-weight: normal;
                background-color: transparent;
                min-width: 120px;
            }
            
            #navBar QPushButton:hover {
                background-color: #6d4c41;
            }
            
            #navBar QPushButton:checked {
                background-color: #8d6e63;
                color: #fff8e1;
                font-weight: bold;
            }
            
            #headerSeparator {
                color: #6d4c41;
                height: 1px;
            }
            
            #contentContainer {
                background-color: #d7ccc8;
            }
            
            #contentStack {
                background-color: #efebe9;
                border: 1px solid #bcaaa4;
                border-radius: 5px;
            }
            
            #cartButton, #userButton {
                background-color: #795548;
                color: #efebe9;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            
            #cartButton:hover, #userButton:hover {
                background-color: #8d6e63;
            }
            
            #userMenu {
                background-color: #efebe9;
                border: 1px solid #bcaaa4;
                border-radius: 4px;
                padding: 5px 0;
            }
            
            #userMenu::item {
                padding: 8px 20px;
                color: #3e2723;
            }
            
            #userMenu::item:selected {
                background-color: #8d6e63;
                color: #efebe9;
            }
            
            QMessageBox {
                background-color: #efebe9;
            }
            
            QMessageBox QPushButton {
                background-color: #795548;
                color: #efebe9;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            
            QMessageBox QPushButton:hover {
                background-color: #8d6e63;
            }
            
            QDialog {
                background-color: #efebe9;
            }
            
            /* Style cho tables và các phần tử khác */
            QTableView {
                alternate-background-color: #d7ccc8;
                background-color: #efebe9;
                border: 1px solid #bcaaa4;
                border-radius: 3px;
            }
            
            QTableView::item:selected {
                background-color: #8d6e63;
                color: #efebe9;
            }
            
            QHeaderView::section {
                background-color: #5d4037;
                color: #d7ccc8;
                padding: 5px;
                border: 1px solid #4e342e;
            }
            
            QLineEdit, QComboBox, QSpinBox, QDateEdit {
                background-color: #f5f5f5;
                border: 1px solid #bcaaa4;
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
            }
            
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {
                border: 1px solid #6d4c41;
            }
            
            QPushButton {
                background-color: #795548;
                color: #efebe9;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                margin: 2px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #8d6e63;
            }
            
            QPushButton:pressed {
                background-color: #6d4c41;
            }
            
            QLabel {
                color: #3e2723;
            }
            
            QGroupBox {
                border: 1px solid #bcaaa4;
                border-radius: 4px;
                margin-top: 15px;
                font-weight: bold;
                color: #4e342e;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistency across platforms
    window = CafeManagementUI()
    sys.exit(app.exec())