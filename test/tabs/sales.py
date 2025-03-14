from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QHBoxLayout, QScrollArea, QGridLayout, QFrame, QMessageBox,
                             QSizePolicy, QSpacerItem)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, Signal
import os
from database_connection import connect_db

class ProductCard(QFrame):
    add_to_cart_signal = Signal(str, str, float)
    
    def __init__(self, product_id, name, price, image_path):
        super().__init__()
        self.product_id = product_id
        self.product_name = name
        self.product_price = price
        self.image_path = image_path  # Lưu lại image_path
        
        self.setFixedSize(200, 280)  # Tăng kích thước thẻ sản phẩm
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("""
            ProductCard {
                border: 1px solid #ddd;
                border-radius: 10px;
                background-color: white;
            }
            ProductCard:hover {
                border: 1px solid #2196F3;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                transform: translateY(-2px);
                transition: all 0.3s ease;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Hình ảnh
        self.image_label = QLabel()
        self.image_label.setFixedSize(180, 140)  # Kích thước hình ảnh lớn hơn
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #eee; border-radius: 5px; background-color: #f9f9f9;")
        
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                180, 140,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            no_image_label = QLabel("Không có\nhình ảnh")
            no_image_label.setFont(QFont("Arial", 10))
            no_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_image_label.setStyleSheet("color: #999;")
            no_image_layout = QVBoxLayout(self.image_label)
            no_image_layout.addWidget(no_image_label)
        
        layout.addWidget(self.image_label)
        
        # Tên sản phẩm
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setFixedHeight(42)  # Chiều cao cố định cho tên
        name_label.setStyleSheet("color: #333;")
        layout.addWidget(name_label)
        
        # Đường kẻ ngăn cách
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #eee;")
        layout.addWidget(separator)
        
        # Giá
        price_label = QLabel(f"{price:,.0f} VNĐ")
        price_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        price_label.setStyleSheet("color: #e53935;")  # Màu đỏ cho giá
        layout.addWidget(price_label)
        
        # Nút thêm vào giỏ hàng
        add_button = QPushButton("+ Thêm vào giỏ hàng")
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 9pt;
                border: none;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
        """)
        add_button.clicked.connect(self.add_to_cart)
        layout.addWidget(add_button)
    
    def add_to_cart(self):
        self.add_to_cart_signal.emit(self.product_id, self.product_name, self.product_price)


class SalesTab(QWidget):
    def __init__(self, cart_tab=None):
        super().__init__()
        self.conn = None
        self.cursor = None
        self.cart_tab = cart_tab
        self.products = []
        self.filtered_products = []
        
        self.initUI()
        self.connectDB()
        self.loadProducts()
    
    # Thêm phương thức mới này
    def setCartTab(self, cart_tab):
        self.cart_tab = cart_tab
    
    def initUI(self):
        # Layout chính
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
    
        # Tiêu đề
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
    
        title = QLabel("Danh Sách Sản Phẩm")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setStyleSheet("color: #333;")
        title_layout.addWidget(title)
    
        # Đường kẻ phân cách
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #ddd;")
        title_layout.addWidget(separator)
    
        main_layout.addWidget(title_container)
    
        # Phần tìm kiếm và các nút điều khiển
        search_container = QWidget()
        search_container.setStyleSheet("background-color: #f5f5f5; border-radius: 8px;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 15, 15, 15)
    
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm sản phẩm...")
        self.search_input.setMinimumHeight(38)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
    
        search_button = QPushButton("Tìm kiếm")
        search_button.setMinimumHeight(38)
        search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        search_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10pt;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        search_button.clicked.connect(self.searchProducts)
        
        # Thêm nút làm mới
        refresh_button = QPushButton("Làm mới")
        refresh_button.setMinimumHeight(38)
        refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #FF9800;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10pt;
                border: none;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        refresh_button.clicked.connect(self.refreshData)
    
        # Thêm widget vào layout tìm kiếm
        search_layout.addWidget(self.search_input, 3)  # Stretch factor
        search_layout.addWidget(search_button)
        search_layout.addWidget(refresh_button)
    
        main_layout.addWidget(search_container)
    
        # Tạo scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
         # Container cho sản phẩm - cố định width cho chính xác 5 sản phẩm
        self.products_container = QWidget()
        # Thiết lập kích thước tối thiểu để đảm bảo có thể hiển thị 5 sản phẩm trên một hàng
        min_width = 5 * 200 + 4 * 20  # 5 sản phẩm (200px) + 4 khoảng cách (20px)
        self.products_container.setMinimumWidth(min_width)
    
        # Container wrapper để căn giữa
        self.wrapper_container = QWidget()
        wrapper_layout = QHBoxLayout(self.wrapper_container)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        # Thêm stretch bên trái để đẩy từ bên trái
        wrapper_layout.addStretch(1)
        wrapper_layout.addWidget(self.products_container)
        # Thêm stretch bên phải để đẩy từ bên phải
        wrapper_layout.addStretch(1)
    
        # Layout grid cho sản phẩm
        self.products_layout = QGridLayout(self.products_container)
        self.products_layout.setSpacing(20)  # Tăng khoảng cách giữa sản phẩm
        self.products_layout.setContentsMargins(0, 0, 0, 20)  # Thêm padding ở dưới
        # Thay đổi căn lề từ AlignLeft sang AlignHCenter
        self.products_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    
        self.scroll_area.setWidget(self.wrapper_container)
        main_layout.addWidget(self.scroll_area, 1)
        
        # Thêm label trạng thái cho cập nhật
        self.status_label = QLabel("Dữ liệu được cập nhật lần cuối: Chưa có")
        self.status_label.setStyleSheet("color: #757575; font-size: 9pt;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.status_label)
    
        # Thêm thông tin dưới chân
        footer = QLabel("Heloo Anh Chị Em - Mời ANh Chị Em Lựa Hàng")
        footer.setStyleSheet("color: #757575; font-size: 9pt;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)
    
    def connectDB(self):
        self.conn = connect_db()
        if self.conn is None:
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối database!")
            return
        self.cursor = self.conn.cursor()
    
    def loadProducts(self):
        if not self.cursor:
            return
            
        try:
            # Đóng và mở lại kết nối để đảm bảo dữ liệu mới nhất
            if self.conn and hasattr(self.conn, 'close'):
                self.connectDB()
                
            self.cursor.execute("SELECT id, name, price, stock, image_path FROM products ORDER BY name")
            self.products = self.cursor.fetchall()
            self.filtered_products = self.products.copy()
            self.displayProducts()
            
            # Cập nhật thời gian làm mới
            import datetime
            current_time = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            self.status_label.setText(f"Dữ liệu được cập nhật lần cuối: {current_time}")
        except Exception as err:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu sản phẩm: {str(err)}")
    
    def displayProducts(self):
        # Xóa sản phẩm hiện tại
        for i in reversed(range(self.products_layout.count())):
            item = self.products_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            elif item.spacerItem():
                self.products_layout.removeItem(item)
        
        # Cố định 5 sản phẩm mỗi hàng
        products_per_row = 5
        
        # Hiển thị sản phẩm trong grid
        for i, product in enumerate(self.filtered_products):
            product_id, name, price, stock, image_path = product
            
            row = i // products_per_row
            col = i % products_per_row
            
            product_card = ProductCard(product_id, name, price, image_path)
            product_card.add_to_cart_signal.connect(self.addToCart)
            
            self.products_layout.addWidget(product_card, row, col)
        
        # Thêm thông báo nếu không có sản phẩm
        if not self.filtered_products:
            no_products_label = QLabel("Không có sản phẩm nào")
            no_products_label.setStyleSheet("""
                font-size: 14pt;
                color: #757575;
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 20px;
            """)
            no_products_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_layout.addWidget(no_products_label, 0, 0, 1, 5)
        
        # Thêm spacer ở cuối để đẩy tất cả lên trên
        self.products_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 
                               (len(self.filtered_products) - 1) // products_per_row + 1, 0)
    
    def searchProducts(self):
        search_term = self.search_input.text().strip().lower()
        
        if not search_term:
            self.resetSearch()
            return
        
        self.filtered_products = [
            product for product in self.products 
            if search_term in product[1].lower()  # product[1] là tên sản phẩm
        ]
        
        self.displayProducts()
        
        # Hiển thị thông báo nếu không tìm thấy sản phẩm
        if not self.filtered_products:
            no_result_msg = QMessageBox()
            no_result_msg.setIcon(QMessageBox.Icon.Information)
            no_result_msg.setWindowTitle("Thông báo")
            no_result_msg.setText("Không tìm thấy sản phẩm nào phù hợp!")
            no_result_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            no_result_msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QPushButton {
                    padding: 5px 15px;
                    background-color: #2196F3;
                    color: white;
                    border-radius: 4px;
                    min-width: 60px;
                    min-height: 25px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            no_result_msg.exec()
    
    def resetSearch(self):
        self.search_input.clear()
        self.filtered_products = self.products.copy()
        self.displayProducts()
    
    # Phương thức làm mới dữ liệu
    def refreshData(self):
        # Lưu từ khóa tìm kiếm hiện tại
        current_search = self.search_input.text().strip().lower()
        
        # Tải lại dữ liệu từ cơ sở dữ liệu
        self.loadProducts()
        
        # Nếu đang tìm kiếm, áp dụng lại bộ lọc
        if current_search:
            self.filtered_products = [
                product for product in self.products 
                if current_search in product[1].lower()
            ]
            self.displayProducts()
    
    # Trong phương thức addToCart, cần truyền cả image_path
    def addToCart(self, product_id, name, price):
        # Tìm sản phẩm trong danh sách để lấy image_path
        image_path = None
        for product in self.products:
            if str(product[0]) == product_id:
                image_path = product[4]  # Giả sử vị trí thứ 5 là image_path
                break
                
        if self.cart_tab:
            self.cart_tab.addToCart(product_id, name, price, 1, image_path)
            
            # Tạo thông báo hoạt ảnh
            add_msg = QMessageBox()
            add_msg.setIcon(QMessageBox.Icon.Information)
            add_msg.setWindowTitle("Giỏ hàng")
            add_msg.setText(f"Đã thêm sản phẩm '{name}' vào giỏ hàng!")
            add_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            add_msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QPushButton {
                    padding: 5px 15px;
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 4px;
                    min-width: 60px;
                    min-height: 25px;
                }
                QPushButton:hover {
                    background-color: #388E3C;
                }
            """)
            add_msg.exec()
        else:
            QMessageBox.information(self, "Thông báo", f"Đã thêm '{name}' vào giỏ hàng nhưng cart_tab chưa được khởi tạo!")