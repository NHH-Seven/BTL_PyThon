import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QScrollArea,
                             QSizePolicy, QSpacerItem, QMessageBox)
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor
from PySide6.QtCore import Qt, Signal, Slot
from database_connection import connect_db
from form.invoice_form import InvoiceForm
from datetime import datetime

class CartItem:
    def __init__(self, product_id, name, price, quantity=1, image_path=None):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.image_path = image_path
        
    @property
    def total(self):
        return self.price * self.quantity
        
class CartTab(QWidget):
    orderPlaced = Signal()
    
    def __init__(self):
        super().__init__()
        self.cart_items = []
        self.initUI()
        
    def initUI(self):
        # Áp dụng CSS chung cho widget
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                color: #212529;
            }
            QPushButton {
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                border: none;
            }
            QLabel {
                color: #212529;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header khu vực giỏ hàng
        header_container = QFrame()
        header_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        header_layout = QHBoxLayout(header_container)
        
        # Icon giỏ hàng
        cart_icon_label = QLabel()
        cart_icon_label.setFixedSize(40, 40)
        # Giả định có tệp icon
        # cart_icon_label.setPixmap(QPixmap("icons/cart.png").scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio))
        cart_icon_label.setText("🛒")
        cart_icon_label.setFont(QFont("Arial", 20))
        cart_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Tiêu đề giỏ hàng
        header_label = QLabel("Giỏ Hàng")
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        header_layout.addWidget(cart_icon_label)
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        
        main_layout.addWidget(header_container)
        
        # Khu vực sản phẩm trong giỏ hàng
        products_container = QFrame()
        products_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            QPushButton {
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        products_layout = QVBoxLayout(products_container)
        
        # Scroll area cho các sản phẩm
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        self.cart_layout = QVBoxLayout(scroll_content)
        self.cart_layout.setContentsMargins(0, 0, 0, 0)
        self.cart_layout.setSpacing(10)
        
        # Empty cart message với icon
        empty_cart_container = QWidget()
        empty_layout = QVBoxLayout(empty_cart_container)
        
        empty_icon = QLabel("🛒")
        empty_icon.setFont(QFont("Arial", 48))
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_icon.setStyleSheet("color: #dee2e6;")
        
        self.empty_cart_label = QLabel("Giỏ hàng của bạn đang trống")
        self.empty_cart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_cart_label.setFont(QFont("Arial", 16))
        self.empty_cart_label.setStyleSheet("color: #6c757d; margin: 10px 0;")
        
        empty_subtitle = QLabel("Hãy thêm sản phẩm vào giỏ hàng của bạn")
        empty_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_subtitle.setFont(QFont("Arial", 12))
        empty_subtitle.setStyleSheet("color: #adb5bd;")
        
        empty_layout.addStretch(1)
        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(self.empty_cart_label)
        empty_layout.addWidget(empty_subtitle)
        empty_layout.addStretch(1)
        
        self.cart_layout.addWidget(empty_cart_container)
        
        # Cart items container
        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(10)
        self.cart_layout.addWidget(self.items_container)
        self.items_container.setVisible(False)
        
        scroll.setWidget(scroll_content)
        products_layout.addWidget(scroll)
        
        main_layout.addWidget(products_container, 1)  # Stretch factor
        
        # Summary và action buttons
        summary_container = QFrame()
        summary_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        summary_layout = QVBoxLayout(summary_container)
        
        # Đường kẻ phía trên summary
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("background-color: #e9ecef;")
        summary_layout.addWidget(divider)
        
        # Thông tin tổng
        info_grid = QGridLayout()
        info_grid.setContentsMargins(10, 10, 10, 10)
        info_grid.setSpacing(10)
        
        subtotal_label = QLabel("Tạm tính:")
        subtotal_label.setFont(QFont("Arial", 12))
        self.total_items_label = QLabel("0 sản phẩm")
        self.total_items_label.setFont(QFont("Arial", 12))
        self.total_items_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        info_grid.addWidget(subtotal_label, 0, 0)
        info_grid.addWidget(self.total_items_label, 0, 1)
        
        # Tổng tiền
        total_title = QLabel("Tổng thanh toán:")
        total_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        self.total_price_label = QLabel("0 VNĐ")
        self.total_price_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.total_price_label.setStyleSheet("color: #d35400;")
        self.total_price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        info_grid.addWidget(total_title, 1, 0)
        info_grid.addWidget(self.total_price_label, 1, 1)
        
        summary_layout.addLayout(info_grid)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(10, 20, 10, 10)
        buttons_layout.setSpacing(15)
        
        clear_cart_btn = QPushButton("Xóa Giỏ Hàng")
        clear_cart_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_cart_btn.setIcon(QIcon("icons/trash.png"))
        clear_cart_btn.clicked.connect(self.clearCart)
        
        checkout_btn = QPushButton("Thanh Toán")
        checkout_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        checkout_btn.setIcon(QIcon("icons/checkout.png"))
        checkout_btn.clicked.connect(self.checkout)
        
        buttons_layout.addWidget(clear_cart_btn)
        buttons_layout.addWidget(checkout_btn)
        
        summary_layout.addLayout(buttons_layout)
        main_layout.addWidget(summary_container)
        
    def refreshCart(self):
        # Xóa các item hiện tại
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if not self.cart_items:
            self.empty_cart_label.parentWidget().setVisible(True)
            self.items_container.setVisible(False)
            self.total_items_label.setText("0 sản phẩm")
            self.total_price_label.setText("0 VNĐ")
            return
        
        self.empty_cart_label.parentWidget().setVisible(False)
        self.items_container.setVisible(True)
        
        total_price = 0
        total_items = 0
        
        # Thêm các sản phẩm vào giỏ hàng
        for index, item in enumerate(self.cart_items):
            item_widget = self.createItemWidget(item, index)
            self.items_layout.addWidget(item_widget)
            total_price += item.total
            total_items += item.quantity
        
        # Cập nhật thông tin tổng
        self.total_items_label.setText(f"{total_items} sản phẩm")
        self.total_price_label.setText(f"{format(total_price, ',.0f')} VNĐ")
    
    def createItemWidget(self, cart_item, index):
        item_frame = QFrame()
        item_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e9ecef;
            }
            QFrame:hover {
                border: 1px solid #dee2e6;
                background-color: #f8f9fa;
            }
        """)
        
        # Thay đổi màu nền cho mỗi hàng xen kẽ
        if index % 2 == 0:
            item_frame.setStyleSheet(item_frame.styleSheet() + "background-color: #fcfcfc;")
        
        layout = QHBoxLayout(item_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Ảnh sản phẩm với đường viền và góc bo tròn
        image_container = QFrame()
        image_container.setFixedSize(100, 100)
        image_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e9ecef;
                padding: 5px;
            }
        """)
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        image_label = QLabel()
        if cart_item.image_path and os.path.exists(cart_item.image_path):
            pixmap = QPixmap(cart_item.image_path)
            scaled_pixmap = pixmap.scaled(
                90, 90,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(scaled_pixmap)
        else:
            image_label.setText("🖼️")
            image_label.setFont(QFont("Arial", 36))
            image_label.setStyleSheet("color: #dee2e6;")
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        image_layout.addWidget(image_label)
        layout.addWidget(image_container)
        
        # Thông tin sản phẩm
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        name_label = QLabel(cart_item.name)
        name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        name_label.setWordWrap(True)
        
        price_layout = QHBoxLayout()
        price_caption = QLabel("Đơn giá:")
        price_caption.setFont(QFont("Arial", 12))
        price_caption.setStyleSheet("color: #6c757d;")
        
        price_value = QLabel(f"{format(cart_item.price, ',.0f')} VNĐ")
        price_value.setFont(QFont("Arial", 12))
        price_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        price_layout.addWidget(price_caption)
        price_layout.addStretch()
        price_layout.addWidget(price_value)
        
        # Thành tiền
        total_layout = QHBoxLayout()
        total_caption = QLabel("Thành tiền:")
        total_caption.setFont(QFont("Arial", 12))
        total_caption.setStyleSheet("color: #6c757d;")
        
        total_value = QLabel(f"{format(cart_item.total, ',.0f')} VNĐ")
        total_value.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        total_value.setStyleSheet("color: #e67e22;")
        total_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        total_layout.addWidget(total_caption)
        total_layout.addStretch()
        total_layout.addWidget(total_value)
        
        info_layout.addWidget(name_label)
        info_layout.addLayout(price_layout)
        info_layout.addLayout(total_layout)
        info_layout.addStretch()
        
        layout.addLayout(info_layout, 1)  # stretch factor
        
        # Điều khiển số lượng với thiết kế mới
        qty_container = QFrame()
        qty_container.setFixedHeight(36)
        qty_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 18px;
                border: 1px solid #dee2e6;
            }
        """)
        
        qty_layout = QHBoxLayout(qty_container)
        qty_layout.setContentsMargins(2, 2, 2, 2)
        qty_layout.setSpacing(0)
        
        decrease_btn = QPushButton("-")
        decrease_btn.setFixedSize(32, 32)
        decrease_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        decrease_btn.setStyleSheet("""
            QPushButton {
                background-color: #e9ecef;
                color: #495057;
                border-radius: 16px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #dee2e6;
            }
        """)
        decrease_btn.clicked.connect(lambda: self.updateItemQuantity(cart_item, -1))
        
        qty_label = QLabel(str(cart_item.quantity))
        qty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qty_label.setFixedWidth(36)
        qty_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        increase_btn = QPushButton("+")
        increase_btn.setFixedSize(32, 32)
        increase_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        increase_btn.setStyleSheet("""
            QPushButton {
                background-color: #e9ecef;
                color: #495057;
                border-radius: 16px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #dee2e6;
            }
        """)
        increase_btn.clicked.connect(lambda: self.updateItemQuantity(cart_item, 1))
        
        qty_layout.addWidget(decrease_btn)
        qty_layout.addWidget(qty_label)
        qty_layout.addWidget(increase_btn)
        
        actions_layout = QVBoxLayout()
        actions_layout.addWidget(qty_container)
        actions_layout.addStretch()
        
        # Nút xóa với thiết kế mới
        remove_btn = QPushButton("Xóa")
        remove_btn.setToolTip("Xóa sản phẩm")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #dc3545;
                border: 1px solid #dc3545;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #dc3545;
                color: white;
            }
        """)
        remove_btn.clicked.connect(lambda: self.removeItemFromCart(cart_item))
        
        actions_layout.addWidget(remove_btn)
        layout.addLayout(actions_layout)
        
        return item_frame
    
    def addToCart(self, product_id, name, price, quantity=1, image_path=None):
        # Kiểm tra sản phẩm đã có trong giỏ hàng chưa
        for item in self.cart_items:
            if item.product_id == product_id:
                item.quantity += quantity
                self.refreshCart()
                return
        
        # Thêm sản phẩm mới
        new_item = CartItem(product_id, name, price, quantity, image_path)
        self.cart_items.append(new_item)
        self.refreshCart()
    
    def updateItemQuantity(self, cart_item, change):
        new_qty = max(1, cart_item.quantity + change)  # Đảm bảo số lượng ít nhất là 1
        cart_item.quantity = new_qty
        self.refreshCart()
    
    def removeItemFromCart(self, cart_item):
        self.cart_items.remove(cart_item)
        self.refreshCart()
    
    def clearCart(self):
        if not self.cart_items:
            return
            
        # Dialog xác nhận xóa với thiết kế mới
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Xác nhận")
        message_box.setText("Bạn có chắc chắn muốn xóa tất cả sản phẩm trong giỏ hàng?")
        message_box.setIcon(QMessageBox.Icon.Question)
        message_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Thiết lập nút
        yes_button = message_box.button(QMessageBox.StandardButton.Yes)
        yes_button.setText("Có, xóa tất cả")
        no_button = message_box.button(QMessageBox.StandardButton.No)
        no_button.setText("Không, giữ lại")
        
        # Thiết lập style sheet
        message_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton[text="Có, xóa tất cả"] {
                background-color: #dc3545;
                color: white;
            }
            QPushButton[text="Không, giữ lại"] {
                background-color: #6c757d;
                color: white;
            }
        """)
        
        reply = message_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            self.cart_items.clear()
            self.refreshCart()
    
    def checkout(self):
        if not self.cart_items:
            QMessageBox.information(self, "Thông báo", "Giỏ hàng trống!")
            return
        
        total_amount = sum(item.total for item in self.cart_items)
        
        # Hiển thị form thanh toán
        invoice_form = InvoiceForm(self, total_amount)
        if invoice_form.exec():
            # Nếu form được chấp nhận, lưu đơn hàng với thông tin khách hàng
            self.saveOrder(
                total_amount, 
                invoice_form.customer_name,
                invoice_form.phone_number,
                invoice_form.payment_method
            )
    
    def saveOrder(self, total_amount, customer_name, phone_number, payment_method):
        conn = connect_db()
        if not conn:
            QMessageBox.critical(self, "Lỗi kết nối", "Không thể kết nối đến cơ sở dữ liệu!")
            return False
    
        try:
            cursor = conn.cursor()
    
            # Tạo ID đơn hàng duy nhất với format ORD + số
            import uuid
            import datetime
        
            # Tạo ID đơn hàng dạng ORD + ngày tháng năm + số ngẫu nhiên
            today = datetime.datetime.now().strftime("%y%m%d")
            random_suffix = str(uuid.uuid4().int)[:4]
            order_id = f"ORD{today}{random_suffix}"
        
            # Lấy ngày hiện tại
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
            # Kiểm tra dữ liệu đầu vào
            if not customer_name or not phone_number:
                QMessageBox.warning(self, "Thông tin thiếu", "Vui lòng nhập đầy đủ thông tin khách hàng!")
                return False
        
            # Kiểm tra số lượng sản phẩm có đủ trong kho
            for item in self.cart_items:
                cursor.execute("SELECT stock FROM products WHERE id = %s", (item.product_id,))
                result = cursor.fetchone()
                if not result:
                    QMessageBox.warning(self, "Lỗi", f"Sản phẩm {item.name} không tồn tại trong hệ thống!")
                    return False
            
                current_stock = result[0]
                if current_stock < item.quantity:
                    QMessageBox.warning(self, "Hết hàng", 
                        f"Sản phẩm '{item.name}' chỉ còn {current_stock} sản phẩm trong kho, không đủ số lượng {item.quantity}!")
                    return False
    
            # Tạo đơn hàng không sử dụng user_id để tránh lỗi khóa ngoại
            cursor.execute("""
                INSERT INTO orders (id, customer_name, phone_number, total_amount, order_date, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (order_id, customer_name, phone_number, total_amount, current_date, payment_method))
    
            # Thêm các sản phẩm vào đơn hàng
            for item in self.cart_items:
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item.product_id, item.quantity, item.price))
    
            # Cập nhật số lượng tồn kho
            for item in self.cart_items:
                cursor.execute("""
                    UPDATE products
                    SET stock = stock - %s
                    WHERE id = %s
                """, (item.quantity, item.product_id))
    
            # Tạo hóa đơn
            import random
            invoice_id = f"INV{today}{random.randint(1000, 9999)}"
        
            cursor.execute("""
                INSERT INTO invoices (id, order_id, customer_name, phone_number, total_amount, payment_method, invoice_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (invoice_id, order_id, customer_name, phone_number, total_amount, payment_method, current_date))
        
            conn.commit()
    
            # Thông báo thành công với thiết kế mới
            success_box = QMessageBox(self)
            success_box.setWindowTitle("Thành công")
            success_box.setText("Đơn hàng của bạn đã được thanh toán thành công!")
            success_box.setInformativeText(f"Mã đơn hàng: #{order_id}")
            success_box.setIcon(QMessageBox.Icon.Information)
            success_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    
            success_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
            """)
    
            success_box.exec()
    
            # Xóa giỏ hàng sau khi đặt hàng thành công
            self.cart_items.clear()
            self.refreshCart()
    
            # Phát tín hiệu đơn hàng đã được đặt
            self.orderPlaced.emit()
    
            return True
    
        except Exception as e:
            conn.rollback()
            error_message = str(e)
            print(f"Lỗi khi tạo đơn hàng: {error_message}")
    
            # Hiển thị thông báo lỗi chi tiết hơn
            error_box = QMessageBox(self)
            error_box.setWindowTitle("Lỗi khi tạo đơn hàng")
            error_box.setText("Không thể tạo đơn hàng do lỗi hệ thống.")
            error_box.setDetailedText(f"Chi tiết lỗi: {error_message}")
            error_box.setIcon(QMessageBox.Icon.Critical)
            error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_box.exec()
    
            return False
        finally:
            conn.close()