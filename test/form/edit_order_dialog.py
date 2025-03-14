from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTableWidget, 
                              QPushButton, QHBoxLayout, QTableWidgetItem, QHeaderView,
                              QMessageBox, QWidget, QGridLayout, QLineEdit,
                              QComboBox, QSpinBox, QDoubleSpinBox, QDateTimeEdit)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, QDateTime
from database_connection import connect_db
from datetime import datetime

class EditOrderDialog(QDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        self.parent = parent
        self.setWindowTitle(f"Sửa đơn hàng #{order_id}")
        self.setMinimumSize(600, 500)
        self.initUI()
        self.loadOrderData()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Customer information section
        info_container = QWidget()
        info_container.setStyleSheet("""
            background-color: #E3F2FD;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
        """)
        info_layout = QGridLayout(info_container)
        
        # Labels and input fields
        info_layout.addWidget(QLabel("Mã đơn hàng:"), 0, 0)
        self.id_label = QLabel(f"#{self.order_id}")
        self.id_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(self.id_label, 0, 1)
        
        info_layout.addWidget(QLabel("Khách hàng:"), 1, 0)
        self.customer_input = QLineEdit()
        info_layout.addWidget(self.customer_input, 1, 1)
        
        info_layout.addWidget(QLabel("Số điện thoại:"), 2, 0)
        self.phone_input = QLineEdit()
        info_layout.addWidget(self.phone_input, 2, 1)
        
        info_layout.addWidget(QLabel("Ngày đặt:"), 3, 0)
        self.date_input = QDateTimeEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy hh:mm")
        info_layout.addWidget(self.date_input, 3, 1)
        
        info_layout.addWidget(QLabel("Phương thức thanh toán:"), 4, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Tiền mặt", "Chuyển khoản", "Thẻ tín dụng", "Momo"])
        info_layout.addWidget(self.status_combo, 4, 1)
        
        layout.addWidget(info_container)
        
        # Order items table
        items_label = QLabel("Sản phẩm trong đơn hàng:")
        items_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(items_label)
        
        self.items_table = QTableWidget(0, 6)  # Added a column for editing quantity
        self.items_table.setHorizontalHeaderLabels([
            "Mã SP", "Tên sản phẩm", "Đơn giá", "Số lượng", "Thành tiền", "Thao tác"
        ])
        
        # Adjust column widths
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.items_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #E3F2FD;
                padding: 5px;
                border: 1px solid #BBDEFB;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.items_table)
        
        # Total amount (calculated automatically)
        self.total_label = QLabel("Tổng tiền: 0 VNĐ")
        self.total_label.setStyleSheet("color: #d35400; font-weight: bold;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.total_label)
        
        # Buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        
        save_button = QPushButton("Lưu thay đổi")
        save_button.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        save_button.clicked.connect(self.saveChanges)
        
        cancel_button = QPushButton("Hủy")
        cancel_button.setStyleSheet("""
            background-color: #9E9E9E;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addWidget(button_container)
    
    def loadOrderData(self):
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get order information
                cursor.execute("""
                    SELECT customer_name, phone_number, order_date, status, total_amount
                    FROM orders
                    WHERE id = %s
                """, (self.order_id,))
                
                order_info = cursor.fetchone()
                if not order_info:
                    QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin đơn hàng!")
                    self.close()
                    return
                
                customer_name, phone, date, status, total = order_info
                
                # Set form values
                self.customer_input.setText(customer_name)
                self.phone_input.setText(phone)
                
                # Handle date conversion
                if isinstance(date, str):
                    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                else:
                    date_obj = date
                qdatetime = QDateTime(date_obj.year, date_obj.month, date_obj.day, 
                                    date_obj.hour, date_obj.minute, date_obj.second)
                self.date_input.setDateTime(qdatetime)
                
                # Set payment method
                index = self.status_combo.findText(status)
                if index >= 0:
                    self.status_combo.setCurrentIndex(index)
                else:
                    # Add the status if it's not in the predefined list
                    self.status_combo.addItem(status)
                    self.status_combo.setCurrentText(status)
                
                # Get order items
                cursor.execute("""
                    SELECT oi.product_id, p.name, oi.price, oi.quantity, (oi.price * oi.quantity) as item_total
                    FROM order_items oi
                    JOIN products p ON p.id = oi.product_id
                    WHERE oi.order_id = %s
                """, (self.order_id,))
                
                items = cursor.fetchall()
                
                # Populate items table
                self.items_table.setRowCount(len(items))
                
                for row_idx, item in enumerate(items):
                    product_id, name, price, quantity, item_total = item
                    
                    # Create table items
                    id_item = QTableWidgetItem(str(product_id))
                    name_item = QTableWidgetItem(name)
                    price_item = QTableWidgetItem(f"{format(price, ',.0f')} VNĐ")
                    
                    # Create spin box for quantity
                    quantity_spin = QSpinBox()
                    quantity_spin.setMinimum(1)
                    quantity_spin.setMaximum(1000)
                    quantity_spin.setValue(quantity)
                    quantity_spin.valueChanged.connect(self.recalculateTotal)
                    
                    total_item = QTableWidgetItem(f"{format(item_total, ',.0f')} VNĐ")
                    
                    # Create remove button
                    remove_button = QPushButton("Xóa")
                    remove_button.setStyleSheet("background-color: #F44336; color: white;")
                    remove_button.clicked.connect(lambda checked, row=row_idx: self.removeItem(row))
                    
                    # Set alignment
                    id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    
                    # Store original price in item data for calculations
                    price_item.setData(Qt.ItemDataRole.UserRole, price)
                    
                    # Set items to table
                    self.items_table.setItem(row_idx, 0, id_item)
                    self.items_table.setItem(row_idx, 1, name_item)
                    self.items_table.setItem(row_idx, 2, price_item)
                    self.items_table.setCellWidget(row_idx, 3, quantity_spin)
                    self.items_table.setItem(row_idx, 4, total_item)
                    self.items_table.setCellWidget(row_idx, 5, remove_button)
                
                # Update total
                self.total_label.setText(f"Tổng tiền: {format(total, ',.0f')} VNĐ")
                
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể tải chi tiết đơn hàng: {str(e)}")
            finally:
                conn.close()
    
    def removeItem(self, row):
        reply = QMessageBox.question(self, "Xác nhận xóa", 
                                    "Bạn có chắc chắn muốn xóa sản phẩm này khỏi đơn hàng?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.items_table.removeRow(row)
            self.recalculateTotal()
    
    def recalculateTotal(self):
        total = 0
        
        for row in range(self.items_table.rowCount()):
            price_item = self.items_table.item(row, 2)
            price = price_item.data(Qt.ItemDataRole.UserRole)
            
            quantity_spin = self.items_table.cellWidget(row, 3)
            quantity = quantity_spin.value()
            
            item_total = price * quantity
            self.items_table.item(row, 4).setText(f"{format(item_total, ',.0f')} VNĐ")
            
            total += item_total
        
        self.total_label.setText(f"Tổng tiền: {format(total, ',.0f')} VNĐ")
    
    def saveChanges(self):
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Update order information
                cursor.execute("""
                    UPDATE orders 
                    SET customer_name = %s, 
                        phone_number = %s, 
                        order_date = %s, 
                        status = %s, 
                        total_amount = %s
                    WHERE id = %s
                """, (
                    self.customer_input.text(),
                    self.phone_input.text(),
                    self.date_input.dateTime().toString("yyyy-MM-dd hh:mm:ss"),
                    self.status_combo.currentText(),
                    float(self.total_label.text().split(":")[1].strip().replace(",", "").replace("VNĐ", "")),
                    self.order_id
                ))
                
                # Delete existing order items
                cursor.execute("DELETE FROM order_items WHERE order_id = %s", (self.order_id,))
                
                for row in range(self.items_table.rowCount()):
                    product_id = self.items_table.item(row, 0).text().strip()  # 🔥 Không convert sang INT!
                    price = self.items_table.item(row, 2).data(Qt.ItemDataRole.UserRole)
                    quantity = self.items_table.cellWidget(row, 3).value()

                    # Kiểm tra product_id có tồn tại trong bảng products không
                    cursor.execute("SELECT COUNT(*) FROM products WHERE id = %s", (product_id,))
                    exists = cursor.fetchone()[0]
                    
                    if exists:  # ✅ Chỉ INSERT nếu product_id tồn tại
                        cursor.execute("""
                            INSERT INTO order_items (order_id, product_id, price, quantity)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            self.order_id,
                            product_id,
                            price,
                            quantity
                        ))
                    else:
                        QMessageBox.warning(self, "Lỗi", f"Sản phẩm {product_id} không tồn tại, không thể thêm vào đơn hàng!")

                
                # Commit the transaction
                conn.commit()
                
                QMessageBox.information(self, "Thành công", 
                                      f"Đã cập nhật đơn hàng #{self.order_id}")
                
                # Refresh the parent dialog
                if self.parent:
                    self.parent.loadOrderDetails()
                
                self.accept()
                
            except Exception as e:
                conn.rollback()
                QMessageBox.warning(self, "Lỗi", f"Không thể cập nhật đơn hàng: {str(e)}")
            finally:
                conn.close()