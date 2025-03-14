from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QComboBox, QPushButton, QFormLayout,
                              QGroupBox, QMessageBox)
from PySide6.QtCore import Qt
from datetime import datetime

class InvoiceForm(QDialog):
    def __init__(self, parent=None, total_amount=0):
        super().__init__(parent)
        self.total_amount = total_amount
        self.customer_name = ""
        self.phone_number = ""
        self.payment_method = "Tiền mặt"  # Default payment method
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Hóa Đơn Thanh Toán")
        self.setMinimumWidth(450)
        
        main_layout = QVBoxLayout(self)
        
        # Invoice header
        header_label = QLabel("HÓA ĐƠN THANH TOÁN")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1976D2;
            padding: 10px;
        """)
        main_layout.addWidget(header_label)
        
        # Date and Invoice number
        info_layout = QHBoxLayout()
        current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        date_label = QLabel(f"Ngày: {current_date}")
        info_layout.addWidget(date_label)
        info_layout.addStretch()
        main_layout.addLayout(info_layout)
        
        # Form layout for customer information
        form_group = QGroupBox("Thông tin khách hàng")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập tên khách hàng...")
        form_layout.addRow(QLabel("Tên khách hàng:"), self.name_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Nhập số điện thoại...")
        form_layout.addRow(QLabel("Số điện thoại:"), self.phone_input)
        
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Tiền mặt", "Chuyển khoản", "Thẻ tín dụng", "Momo"])
        form_layout.addRow(QLabel("Phương thức thanh toán:"), self.payment_combo)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Total amount
        total_box = QGroupBox("Thông tin thanh toán")
        total_layout = QVBoxLayout()
        
        formatted_total = format(self.total_amount, ",.0f")
        total_label = QLabel(f"Tổng tiền: {formatted_total} VNĐ")
        total_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2E7D32;
            padding: 5px;
        """)
        total_layout.addWidget(total_label)
        
        total_box.setLayout(total_layout)
        main_layout.addWidget(total_box)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            background-color: #F44336;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        
        confirm_btn = QPushButton("Xác nhận thanh toán")
        confirm_btn.clicked.connect(self.confirmPayment)
        confirm_btn.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        """)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(confirm_btn)
        
        main_layout.addLayout(button_layout)
    
    def confirmPayment(self):
        # Validate inputs
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên khách hàng!")
            return
            
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số điện thoại!")
            return
        
        # Save information
        self.customer_name = self.name_input.text().strip()
        self.phone_number = self.phone_input.text().strip()
        self.payment_method = self.payment_combo.currentText()
        
        # Close dialog with accept result
        self.accept()