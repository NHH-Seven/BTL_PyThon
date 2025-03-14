from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class MenuItemCard(QFrame):
    def __init__(self, item_data):
        super().__init__()
        self.initUI(item_data)
    
    def initUI(self, item_data):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 12px;
                border: 1px solid #E0E0E0;
            }
            QFrame:hover {
                border: 1px solid #4A90E2;
                background-color: #F5F5F5;
            }
            QLabel {
                padding: 4px;
            }
            .price-label {
                color: #2E7D32;
                font-weight: bold;
            }
            .status-label {
                color: #1565C0;
            }
        """)
        self.setFixedSize(220, 180)
        
        name_label = QLabel(item_data[1])
        name_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        price_label = QLabel(f"Giá: {format(float(item_data[2]), ',.0f')} VNĐ")
        price_label.setProperty('class', 'price-label')
        
        status = "Còn hàng" if int(item_data[3]) > 0 else "Hết hàng"
        status_color = "#2E7D32" if status == "Còn hàng" else "#C62828"
        status_label = QLabel(f"Trạng thái: {status}")
        status_label.setStyleSheet(f"color: {status_color}")
        
        category_label = QLabel(f"Danh mục: {item_data[4]}" if len(item_data) > 4 else "Danh mục: Chưa phân loại")
        
        layout.addWidget(name_label)
        layout.addWidget(price_label)
        layout.addWidget(status_label)
        layout.addWidget(category_label)