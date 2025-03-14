import os
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

def createProductCard(product):
    card = QFrame()
    card.setStyleSheet("""
        QFrame {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #E0E0E0;
            min-width: 250px;
            max-width: 300px;
        }
        QFrame:hover {
            border: 1px solid #4A90E2;
            background-color: #F5F5F5;
        }
        QLabel {
            padding: 5px;
        }
        .price-label {
            color: #2E7D32;
            font-weight: bold;
        }
    """)
    
    layout = QVBoxLayout(card)
    
    # Hình ảnh sản phẩm
    image_label = QLabel()
    if product[4] and os.path.exists(product[4]):  # image_path
        pixmap = QPixmap(product[4])
        scaled_pixmap = pixmap.scaled(
            200, 200,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    else:
        image_label.setText("Không có hình ảnh")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    # Thông tin sản phẩm
    name_label = QLabel(product[1])  # name
    name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
    name_label.setWordWrap(True)
    name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    price_label = QLabel(f"Giá: {format(float(product[2]), ',.0f')} VNĐ")  # price
    price_label.setProperty('class', 'price-label')
    price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    status = "Còn hàng" if int(product[3]) > 0 else "Hết hàng"  # stock
    status_color = "#2E7D32" if status == "Còn hàng" else "#C62828"
    status_label = QLabel(f"Trạng thái: {status}")
    status_label.setStyleSheet(f"color: {status_color}")
    status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    layout.addWidget(image_label)
    layout.addWidget(name_label)
    layout.addWidget(price_label)
    layout.addWidget(status_label)
    
    return card