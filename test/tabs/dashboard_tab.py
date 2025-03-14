from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QSizePolicy, QGridLayout, QSpacerItem)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QTimer  # Thêm QTimer

from database_connection import connect_db

class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupTimer()  # Thiết lập timer
        
    def initUI(self):
        # Giữ nguyên phần cũ
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Tiêu đề trang chủ
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("TRANG CHỦ QUẢN LÝ QUÁN CAFE")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #1976D2; margin: 10px;")
        title_layout.addWidget(title_label)
        
        # Phần giới thiệu về quán cafe
        intro_text = """
        <p style='font-size: 16px; line-height: 1.6; text-align: center;'>
        Chào mừng đến với phần mềm quản lý quán cafe của chúng tôi! 
        Hệ thống này giúp bạn quản lý hiệu quả các hoạt động kinh doanh, 
        từ bán hàng, quản lý sản phẩm, đến quản lý nhân viên và thống kê doanh thu.
        </p>
        """
        intro_label = QLabel(intro_text)
        intro_label.setWordWrap(True)
        intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(intro_label)
        
        main_layout.addWidget(title_frame)
        
        # Thống kê tổng quan
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        # Tạo các widget thống kê
        self.stats_widgets = []
        stats_info = [
            ("💰 Doanh Thu Hôm Nay", "0 VND", self.getDailyRevenue),
            ("📦 Đơn Hàng Hôm Nay", "0", self.getDailyOrders),
            ("📊 Doanh Thu Tháng Này", "0 VND", self.getMonthlyRevenue),
            ("🛒 Tổng Đơn Hàng", "0", self.getTotalOrders)
        ]
        
        row, col = 0, 0
        for title, default_value, update_func in stats_info:
            stats_widget = self.createStatsWidget(title, default_value)
            stats_grid.addWidget(stats_widget, row, col)
            self.stats_widgets.append((stats_widget, update_func))
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        main_layout.addLayout(stats_grid)
        
        # Thêm khoảng trống ở cuối
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Thêm thông tin cập nhật
        self.update_info = QLabel("Dữ liệu cập nhật tự động mỗi 30 giây")
        self.update_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_info.setStyleSheet("color: #888; font-style: italic;")
        main_layout.addWidget(self.update_info)
        
        # Cập nhật dữ liệu thống kê lần đầu
        self.updateStats()
    
    def setupTimer(self):
        # Tạo timer để tự động cập nhật dashboard
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.updateStats)
        # Cập nhật mỗi 30 giây (30000 ms) - có thể điều chỉnh thời gian này
        self.update_timer.start(30000)
        print("Đã thiết lập timer cập nhật dữ liệu mỗi 30 giây")
    
    def createStatsWidget(self, title, value):
        # Giữ nguyên phần cũ
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
        """)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        widget.setMinimumHeight(150)
        
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14))
        title_label.setStyleSheet("color: #555;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: #1976D2; margin-top: 10px;")
        value_label.setObjectName("value_label")
        layout.addWidget(value_label)
        
        return widget
    
    def updateStats(self):
        print("Đang cập nhật dữ liệu thống kê...")
        # Lưu thời gian cập nhật cuối cùng
        from datetime import datetime
        last_update = datetime.now().strftime("%H:%M:%S")
        
        # Cập nhật giá trị cho từng widget thống kê
        for idx, (widget, update_func) in enumerate(self.stats_widgets):
            try:
                value = update_func()
                print(f"Widget {idx}: Giá trị mới là {value}")
                
                # Tìm label giá trị bằng ObjectName
                value_label = widget.findChild(QLabel, "value_label")
                if value_label:
                    value_label.setText(value)
                    print(f"Đã cập nhật widget {idx} thành công")
                else:
                    print(f"Không tìm thấy label cho widget {idx}")
            except Exception as e:
                print(f"Lỗi khi cập nhật widget {idx}: {str(e)}")
        
        # Cập nhật thông tin về lần cập nhật cuối
        self.update_info.setText(f"Dữ liệu cập nhật tự động mỗi 30 giây. Cập nhật cuối: {last_update}")
    
    def getDailyRevenue(self):
        # Giữ nguyên phần cũ
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COALESCE(SUM(total_amount), 0) 
                    FROM orders 
                    WHERE DATE(order_date) = DATE(NOW())
                """)
                result = cursor.fetchone()
                print(f"Daily revenue query result: {result}")
                if result and result[0]:
                    revenue = float(result[0])
                    return f"{int(revenue):,} VND"
            except Exception as e:
                print(f"Error getting daily revenue: {str(e)}")
            finally:
                conn.close()
        else:
            print("Không thể kết nối đến cơ sở dữ liệu")
        return "0 VND"
    
    def getMonthlyRevenue(self):
        # Giữ nguyên phần cũ
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COALESCE(SUM(total_amount), 0) 
                    FROM orders 
                    WHERE YEAR(order_date) = YEAR(NOW()) 
                    AND MONTH(order_date) = MONTH(NOW())
                """)
                result = cursor.fetchone()
                print(f"Monthly revenue query result: {result}")
                if result and result[0]:
                    revenue = float(result[0])
                    return f"{int(revenue):,} VND"
            except Exception as e:
                print(f"Error getting monthly revenue: {str(e)}")
            finally:
                conn.close()
        else:
            print("Không thể kết nối đến cơ sở dữ liệu")
        return "0 VND"
    
    def getDailyOrders(self):
        # Giữ nguyên phần cũ
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM orders 
                    WHERE DATE(order_date) = DATE(NOW())
                """)
                result = cursor.fetchone()
                print(f"Daily orders query result: {result}")
                if result:
                    return str(result[0])
            except Exception as e:
                print(f"Error getting daily orders: {str(e)}")
            finally:
                conn.close()
        else:
            print("Không thể kết nối đến cơ sở dữ liệu")
        return "0"
    
    def getTotalOrders(self):
        # Giữ nguyên phần cũ
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM orders")
                result = cursor.fetchone()
                print(f"Total orders query result: {result}")
                if result:
                    return str(result[0])
            except Exception as e:
                print(f"Error getting total orders: {str(e)}")
            finally:
                conn.close()
        else:
            print("Không thể kết nối đến cơ sở dữ liệu")
        return "0"
        
    # Thêm phương thức để dừng timer khi tab không còn được hiển thị
    def hideEvent(self, event):
        # Tạm dừng timer khi tab không hiển thị để tiết kiệm tài nguyên
        self.update_timer.stop()
        super().hideEvent(event)
        
    def showEvent(self, event):
        # Khởi động lại timer khi tab được hiển thị
        self.updateStats()  # Cập nhật ngay lập tức
        self.update_timer.start()
        super().showEvent(event)