from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHBoxLayout, QFrame, QGridLayout, QScrollArea, QPushButton,
    QFileDialog, QMessageBox, QSizePolicy)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QSize
from database_connection import connect_db
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from datetime import datetime
from decimal import Decimal

class StatisticsCard(QFrame):
    def __init__(self, title, value, unit=""):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
                border: 1px solid #E0E0E0;
            }
            QLabel {
                color: #333;
            }
        """)
        layout = QVBoxLayout(self)
        
        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        title_label.setFont(QFont("Arial", 12))
        
        value_label = QLabel(f"{value:,} {unit}")
        value_label.setObjectName("valueLabel")
        value_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Make the card clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class StatisticsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.top_products = []
        self.summary_data = {}
        self.monthly_revenue_visible = False
        self.initUI()
        self.loadStatistics()
    
    def initUI(self):
        # Main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # Remove border
        
        # Create container widget for scroll area
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(20)
        self.container_layout.setContentsMargins(10, 10, 10, 20)  # Add extra bottom margin
        
        # Header with title and export button
        header_layout = QHBoxLayout()
        title = QLabel("Thống Kê Cửa Hàng")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #333;")
        header_layout.addWidget(title)
        
        # Export button
        self.export_btn = QPushButton("Xuất Excel")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b3d;
            }
        """)
        self.export_btn.setMinimumWidth(120)
        self.export_btn.clicked.connect(self.exportToExcel)
        header_layout.addWidget(self.export_btn)
        header_layout.setStretchFactor(title, 3)
        header_layout.setStretchFactor(self.export_btn, 1)
        self.container_layout.addLayout(header_layout)
        # Trong phương thức initUI, thêm nút làm mới bên cạnh nút xuất Excel
        self.refresh_btn = QPushButton("Làm Mới")
        self.refresh_btn.setStyleSheet("""
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #0b7dda;
        }
        QPushButton:pressed {
            background-color: #0a6fc2;
        }
        """)
        self.refresh_btn.setMinimumWidth(120)
        self.refresh_btn.clicked.connect(self.refreshData)
        header_layout.addWidget(self.refresh_btn)
        header_layout.setStretchFactor(title, 3)
        header_layout.setStretchFactor(self.export_btn, 1)
        header_layout.setStretchFactor(self.refresh_btn, 1)
        
        # Statistics Cards in Grid Layout
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
        self.cards = {
            'total_products': StatisticsCard("Tổng số sản phẩm", 0, "sản phẩm"),
            'total_revenue': StatisticsCard("Tổng doanh thu", 0, "VNĐ"),
            'total_inventory': StatisticsCard("Tổng hàng tồn kho", 0, "sản phẩm")
        }
        
        # Đã bỏ thẻ khách hàng, chỉ giữ 3 thống kê
        # Canh giữa tổng hàng tồn kho bằng cách thêm vào cột giữa
        cards_layout.addWidget(self.cards['total_products'], 0, 0)
        cards_layout.addWidget(self.cards['total_revenue'], 0, 1)
        cards_layout.addWidget(self.cards['total_inventory'], 0, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)
        
        # Connect click events to cards
        self.cards['total_revenue'].mousePressEvent = self.toggleMonthlyRevenue
        
        self.container_layout.addLayout(cards_layout)
        
        # Monthly Revenue Chart (hidden by default)
        self.monthly_revenue_frame = QFrame()
        self.monthly_revenue_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.monthly_revenue_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        monthly_revenue_layout = QVBoxLayout(self.monthly_revenue_frame)
        monthly_revenue_layout.setContentsMargins(15, 15, 15, 15)
        
        monthly_revenue_title = QLabel("Doanh Thu Theo Tháng")
        monthly_revenue_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        monthly_revenue_layout.addWidget(monthly_revenue_title)
        
        self.figure_monthly = Figure(figsize=(12, 6), dpi=100)
        self.ax_monthly = self.figure_monthly.add_subplot(111)
        self.canvas_monthly = FigureCanvas(self.figure_monthly)
        self.canvas_monthly.setMinimumHeight(300)
        monthly_revenue_layout.addWidget(self.canvas_monthly)
        
        self.monthly_revenue_frame.setVisible(False)
        self.container_layout.addWidget(self.monthly_revenue_frame)
        
        # Charts Section
        charts_frame = QFrame()
        charts_frame.setFrameShape(QFrame.Shape.StyledPanel)
        charts_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
        """)
        charts_layout = QVBoxLayout(charts_frame)
        charts_layout.setContentsMargins(15, 15, 15, 15)
        
        # Charts Title
        charts_title = QLabel("Biểu Đồ Phân Tích")
        charts_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        charts_layout.addWidget(charts_title)
        
        # Create matplotlib figure for bar chart (replacing pie chart)
        self.figure1 = Figure(figsize=(12, 8), dpi=100)
        self.ax1 = self.figure1.add_subplot(111)
        
        self.canvas1 = FigureCanvas(self.figure1)
        self.canvas1.setMinimumHeight(400)
        self.canvas1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        charts_layout.addWidget(self.canvas1)
        
        self.container_layout.addWidget(charts_frame)
        
        # Detailed Statistics Table in a frame
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Shape.StyledPanel)
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
            QTableWidget {
                border: none;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        # Trong phương thức initUI, thay đổi tiêu đề của bảng
        table_label = QLabel("Chi Tiết Top 5 Sản Phẩm Bán Chạy Nhất")
        table_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        table_layout.addWidget(table_label)

        # Thay đổi tiêu đề cột để phản ánh đúng ý nghĩa của dữ liệu
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(5)
        self.stats_table.setHorizontalHeaderLabels([
            "Danh Mục", "Đã Bán", "Tồn Kho", "Giá", "Doanh Thu"
        ])
        self.stats_table.setMinimumHeight(200)
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setStyleSheet("alternate-background-color: #f5f5f5;")
        table_layout.addWidget(self.stats_table)
        
        self.container_layout.addWidget(table_frame)
        
        # Add a spacer widget at the bottom to ensure everything is scrollable
        spacer = QWidget()
        spacer.setMinimumHeight(20)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.container_layout.addWidget(spacer)
        
        # Set up scroll area and finish layout
        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)
    # Thêm phương thức refreshData
    def refreshData(self):
            # Hiển thị biểu tượng hoặc thông báo đang làm mới
        QMessageBox.information(self, "Đang làm mới", "Đang cập nhật dữ liệu...")
    
        # Làm mới tất cả dữ liệu
        self.loadStatistics()
    
        # Nếu biểu đồ doanh thu theo tháng đang hiển thị, làm mới nó
        if self.monthly_revenue_visible:
            self.loadMonthlyRevenue()
    
    def toggleMonthlyRevenue(self, event):
        self.monthly_revenue_visible = not self.monthly_revenue_visible
        self.monthly_revenue_frame.setVisible(self.monthly_revenue_visible)
        
        # Load monthly revenue data if becoming visible
        if self.monthly_revenue_visible:
            self.loadMonthlyRevenue()
    
    # Sửa lại phương thức loadMonthlyRevenue để lấy dữ liệu từ CSDL
    def loadMonthlyRevenue(self):
        conn = connect_db()
        if not conn:
            return
    
        cursor = conn.cursor()
        try:
        # Lấy dữ liệu doanh thu theo tháng từ bảng orders
            cursor.execute("""
            SELECT 
                DATE_FORMAT(order_date, '%Y-%m') as month,
                SUM(total_amount) as revenue
            FROM 
                orders
            WHERE 
                order_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY 
                DATE_FORMAT(order_date, '%Y-%m')
            ORDER BY 
                month ASC
            """)
        
            monthly_data = cursor.fetchall()
        
            # Tạo danh sách các tháng trong 12 tháng gần nhất
            current_date = datetime.now()
            labels = []
            revenue_map = {}
        
            # Tạo danh sách 12 tháng gần nhất và đặt doanh thu mặc định là 0
            for i in range(11, -1, -1):
                month_date = current_date.replace(day=1) - pd.DateOffset(months=i)
                month_key = month_date.strftime('%Y-%m')
                month_label = f'Tháng {month_date.month}/{month_date.year}'
                labels.append(month_label)
                revenue_map[month_key] = 0
        
            # Cập nhật doanh thu cho các tháng có dữ liệu
            for month_str, revenue in monthly_data:
                if month_str in revenue_map:
                    # Chuyển đổi revenue từ Decimal sang float nếu cần
                    if isinstance(revenue, Decimal):
                        revenue = float(revenue)
                    revenue_map[month_str] = int(revenue)
        
            # Lấy dữ liệu doanh thu theo thứ tự các tháng
            revenue_data = []
            for i in range(11, -1, -1):
                month_date = current_date.replace(day=1) - pd.DateOffset(months=i)
                month_key = month_date.strftime('%Y-%m')
                revenue_data.append(revenue_map[month_key])
        
            # Vẽ biểu đồ
            self.ax_monthly.clear()
            bars = self.ax_monthly.bar(labels, revenue_data, color='#4CAF50')
        
            # Thêm nhãn giá trị trên các cột
            for bar in bars:
                height = bar.get_height()
                if height > 0:  # Chỉ hiển thị nhãn cho các cột có giá trị > 0
                    self.ax_monthly.text(
                        bar.get_x() + bar.get_width()/2.,
                        height + 0.05 * max(revenue_data) if max(revenue_data) > 0 else 1000,
                        f'{int(height):,}',
                        ha='center', va='bottom',
                        rotation=0,
                        fontsize=8
                    )
        
            self.ax_monthly.set_title('Doanh Thu Theo Tháng (VNĐ)', fontsize=12)
            self.ax_monthly.set_ylabel('Doanh Thu (VNĐ)', fontsize=10)
            plt.setp(self.ax_monthly.get_xticklabels(), rotation=45, ha='right', fontsize=8)
        
            # Định dạng trục y để hiển thị giá trị theo nghìn
            self.ax_monthly.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, p: format(int(x), ','))
            )
        
            self.figure_monthly.tight_layout()
            self.canvas_monthly.draw()
        
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu doanh thu theo tháng: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    # Cần thay đổi trong loadStatistics() để lấy dữ liệu sản phẩm bán chạy nhất
    def loadStatistics(self):
        conn = connect_db()
        if not conn:
            return
    
        cursor = conn.cursor()
        try:
        # Tổng số sản phẩm
            cursor.execute("SELECT COUNT(*), SUM(stock) FROM products")
            product_count, total_stock = cursor.fetchone()
            product_count = int(product_count or 0)
            total_stock = int(total_stock or 0)
        
            # Cập nhật các card
            self.cards['total_products'].findChild(QLabel, "valueLabel").setText(f"{product_count:,} sản phẩm")
            self.cards['total_inventory'].findChild(QLabel, "valueLabel").setText(f"{total_stock:,} sản phẩm")
        
            # Tổng doanh thu từ các đơn hàng
            cursor.execute("SELECT SUM(total_amount) FROM orders")
            total_revenue = cursor.fetchone()[0] or 0
            total_revenue = float(total_revenue) if isinstance(total_revenue, Decimal) else total_revenue
            self.cards['total_revenue'].findChild(QLabel, "valueLabel").setText(f"{int(total_revenue):,} VNĐ")
        
            # Lưu dữ liệu tổng quan để xuất Excel
            self.summary_data = {
                'total_products': product_count,
                'total_inventory': total_stock,
                'total_revenue': total_revenue
            }
        
            # Lấy dữ liệu cho các sản phẩm xuất hiện nhiều nhất trong đơn hàng
            # Sử dụng JOIN giữa order_items và products để lấy tên sản phẩm và thông tin liên quan
            cursor.execute("""
                SELECT 
                    p.name, 
                    SUM(oi.quantity) as total_sold, 
                    p.stock,
                    p.price, 
                    SUM(oi.quantity * oi.price) as total_revenue
                FROM 
                    order_items oi
                JOIN 
                    products p ON oi.product_id = p.id
                GROUP BY 
                    oi.product_id
             ORDER BY 
                    total_sold DESC
                LIMIT 5
            """)
            self.top_products = cursor.fetchall()
        
            # Update bar chart (thay thế pie chart)
            names = [p[0] for p in self.top_products]
            revenues = [float(p[4]) if isinstance(p[4], Decimal) else p[4] for p in self.top_products]
        
            self.ax1.clear()
            bars = self.ax1.bar(names, revenues, color='#4CAF50')
        
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                self.ax1.text(
                    bar.get_x() + bar.get_width()/2.,
                    height + 0.05 * max(revenues) if max(revenues) > 0 else 1000,
                    f'{int(height):,}',
                    ha='center', va='bottom',
                    rotation=0,
                    fontsize=10
                )
        
            self.ax1.set_title('Top 5 Sản Phẩm Bán Chạy Nhất', fontsize=12)
            self.ax1.set_ylabel('Doanh Thu (VNĐ)', fontsize=10)
        
            # Rotate x-axis labels for better readability
            plt.setp(self.ax1.get_xticklabels(), rotation=30, ha='right', fontsize=9)
        
            # Format y-axis to show values in thousands
            self.ax1.get_yaxis().set_major_formatter(
                plt.FuncFormatter(lambda x, p: format(int(x), ','))
            )
        
            self.figure1.tight_layout(pad=3.0)
            self.canvas1.draw()
        
            # Update table with modified columns
            self.stats_table.setRowCount(len(self.top_products))
        
            for i, (name, sold_qty, stock, price, revenue) in enumerate(self.top_products):
                revenue = float(revenue) if isinstance(revenue, Decimal) else revenue
                price = float(price) if isinstance(price, Decimal) else price
            
                # Format cells and add data
                name_item = QTableWidgetItem(name)
                name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
                # Số lượng đã bán
                quantity_item = QTableWidgetItem(f"{int(sold_qty):,}")
                quantity_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
                # Tồn kho hiện tại
                stock_item = QTableWidgetItem(f"{int(stock):,}")
                stock_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
                price_item = QTableWidgetItem(f"{int(price):,} VNĐ")
                price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
                revenue_item = QTableWidgetItem(f"{int(revenue):,} VNĐ")
                revenue_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
                self.stats_table.setItem(i, 0, name_item)
                self.stats_table.setItem(i, 1, quantity_item)
                self.stats_table.setItem(i, 2, stock_item)
                self.stats_table.setItem(i, 3, price_item)
                self.stats_table.setItem(i, 4, revenue_item)
        
            # Format table appearance
            self.stats_table.horizontalHeader().setStretchLastSection(True)
            self.stats_table.setColumnWidth(0, 180)  # Name column
            self.stats_table.setColumnWidth(1, 80)   # Sold Quantity column
            self.stats_table.setColumnWidth(2, 80)   # Stock column
            self.stats_table.setColumnWidth(3, 100)  # Price column
            self.stats_table.setColumnWidth(4, 120)  # Revenue column
        
        except Exception as e:
            print(f"Lỗi khi tải thống kê: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def exportToExcel(self):
        try:
            # Chọn vị trí và tên file
            file_name, _ = QFileDialog.getSaveFileName(
                self, 
                "Xuất báo cáo Excel", 
                f"Báo_Cáo_Doanh_Thu_{datetime.now().strftime('%d-%m-%Y')}.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if not file_name:
                return  # Người dùng đã hủy
            
            # Tạo file Excel với pandas
            with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Định dạng tiêu đề
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4CAF50',
                    'color': 'white',
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1
                })
                
                # Định dạng số liệu
                number_format = workbook.add_format({
                    'num_format': '#,##0',
                    'align': 'right'
                })
                
                # Định dạng tiền tệ
                currency_format = workbook.add_format({
                    'num_format': '#,##0 "VNĐ"',
                    'align': 'right'
                })
                
                # ---- Sheet 1: Tổng Quan ----
                df_summary = pd.DataFrame({
                    'Chỉ số': ['Tổng số sản phẩm', 'Tổng hàng tồn kho', 'Tổng doanh thu'],
                    'Giá trị': [
                        self.summary_data['total_products'],
                        self.summary_data['total_inventory'],
                        self.summary_data['total_revenue']
                    ],
                    'Đơn vị': ['sản phẩm', 'sản phẩm', 'VNĐ']
                })
                
                df_summary.to_excel(writer, sheet_name='Tổng Quan', index=False)
                
                # Định dạng Sheet Tổng Quan
                sheet1 = writer.sheets['Tổng Quan']
                sheet1.set_column('A:A', 20)
                sheet1.set_column('B:B', 15)
                sheet1.set_column('C:C', 15)
                
                # Thêm định dạng cho tiêu đề
                for col_num, value in enumerate(df_summary.columns.values):
                    sheet1.write(0, col_num, value, header_format)
                
                # Định dạng giá trị
                for i in range(len(df_summary)):
                    if i == 2:  # Dòng doanh thu
                        sheet1.write(i+1, 1, df_summary.iloc[i, 1], currency_format)
                    else:
                        sheet1.write(i+1, 1, df_summary.iloc[i, 1], number_format)
                
                # ---- Sheet 2: Chi Tiết Sản Phẩm ----
                # Trong phương thức exportToExcel, thay đổi phần tạo DataFrame cho sheet Chi Tiết Sản Phẩm
                if self.top_products:
                # Tạo dataframe từ top_products
                    product_data = []
    
                    for name, sold_qty, stock, price, revenue in self.top_products:
                        product_data.append({
                            'Tên sản phẩm': name,
                            'Đã bán': sold_qty,
                            'Tồn kho': stock,
                            'Đơn giá': price,
                            'Doanh thu': revenue
                        })
    
                    df_products = pd.DataFrame(product_data)
                    df_products.to_excel(writer, sheet_name='Chi Tiết Sản Phẩm', index=False)
    
                    # Định dạng Sheet Chi Tiết
                    sheet2 = writer.sheets['Chi Tiết Sản Phẩm']
                    sheet2.set_column('A:A', 30)
                    sheet2.set_column('B:B', 15)
                    sheet2.set_column('C:C', 15)
                    sheet2.set_column('D:D', 15)
                    sheet2.set_column('E:E', 20)
    
                    # Thêm định dạng cho tiêu đề
                    for col_num, value in enumerate(df_products.columns.values):
                        sheet2.write(0, col_num, value, header_format)
    
                    # Định dạng giá trị
                    for i in range(len(df_products)):
                        sheet2.write(i+1, 1, df_products.iloc[i, 1], number_format)
                        sheet2.write(i+1, 2, df_products.iloc[i, 2], number_format)
                        sheet2.write(i+1, 3, df_products.iloc[i, 3], currency_format)
                        sheet2.write(i+1, 4, df_products.iloc[i, 4], currency_format)
                
                # Cập nhật phần xuất dữ liệu doanh thu theo tháng trong exportToExcel
                # Thay thế phần code hiện tại trong hàm exportToExcel:

                # ---- Sheet 3: Doanh Thu Theo Tháng ----
                if self.monthly_revenue_visible:
                    # Lấy dữ liệu từ biểu đồ doanh thu theo tháng
                    monthly_data = []
    
                    # Lấy dữ liệu từ biểu đồ đã vẽ
                    for i, rect in enumerate(self.ax_monthly.patches):
                        if i < len(self.ax_monthly.get_xticklabels()):
                            month = self.ax_monthly.get_xticklabels()[i].get_text()
                            revenue = rect.get_height()
            
                            monthly_data.append({
                                'Tháng': month,
                                'Doanh Thu': int(revenue)
                            })
    
                    df_monthly = pd.DataFrame(monthly_data)
                    df_monthly.to_excel(writer, sheet_name='Doanh Thu Theo Tháng', index=False)
    
                    # Định dạng Sheet Doanh Thu Theo Tháng
                    sheet3 = writer.sheets['Doanh Thu Theo Tháng']
                    sheet3.set_column('A:A', 15)
                    sheet3.set_column('B:B', 20)
    
                    # Thêm định dạng cho tiêu đề
                    for col_num, value in enumerate(df_monthly.columns.values):
                        sheet3.write(0, col_num, value, header_format)
    
                    # Định dạng giá trị
                    for i in range(len(df_monthly)):
                        sheet3.write(i+1, 1, df_monthly.iloc[i, 1], currency_format)
            
            QMessageBox.information(self, "Xuất Excel thành công", 
                                   f"Đã xuất báo cáo thành công đến:\n{file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi xuất Excel", 
                               f"Đã xảy ra lỗi khi xuất báo cáo: {str(e)}")