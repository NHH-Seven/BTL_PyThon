from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
    QLineEdit, QPushButton, QHBoxLayout, QTableWidgetItem, QMessageBox,
    QFileDialog, QDateEdit, QScrollArea, QGridLayout)
from PySide6.QtGui import QFont, QPixmap, QImage
from PySide6.QtCore import Qt, QDate
import os
import shutil
import pandas as pd
from database_connection import connect_db
from datetime import datetime

class ProductManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = None
        self.cursor = None
        self.selected_image_path = None
        self.image_folder = "product_images"
        self.is_image_section_visible = False
        
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)
            
        self.initUI()
        self.connectDB()
        self.loadProducts()

    def initUI(self):
        # Create main scroll area
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create main container widget
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Tiêu đề
        title = QLabel("Quản Lý Sản Phẩm")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Container cho form và controls
        form_container = QHBoxLayout()

        # Panel bên trái cho form nhập liệu
        left_panel = QVBoxLayout()
        
        # Form nhập liệu
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        
        # Tạo và style các input fields
        self.id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.stock_input = QLineEdit()
        self.import_date = QDateEdit()
        
        # Style cho các input
        input_style = """
            QLineEdit, QDateEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
        """
        for widget in [self.id_input, self.name_input, self.price_input, 
                      self.stock_input, self.import_date]:
            widget.setStyleSheet(input_style)
        
        # Thiết lập placeholder text
        self.id_input.setPlaceholderText("Mã SP")
        self.name_input.setPlaceholderText("Tên SP")
        self.price_input.setPlaceholderText("Giá")
        self.stock_input.setPlaceholderText("Tồn kho")
        
        # Cấu hình DateEdit
        self.import_date.setDisplayFormat("dd/MM/yyyy")
        self.import_date.setDate(QDate.currentDate())
        self.import_date.setCalendarPopup(True)
        
        # Thêm các trường vào form
        labels = ["Mã SP:", "Tên SP:", "Giá:", "Tồn Kho:", "Ngày nhập:"]
        widgets = [self.id_input, self.name_input, self.price_input, 
                  self.stock_input, self.import_date]
        
        for i, (label, widget) in enumerate(zip(labels, widgets)):
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold;")
            form_layout.addWidget(label_widget, i, 0)
            form_layout.addWidget(widget, i, 1)
        
        left_panel.addLayout(form_layout)
        
        # Nút chức năng
        button_layout = QHBoxLayout()
        buttons = [
            ("Thêm", "#4CAF50"),
            ("Sửa", "#2196F3"),
            ("Xóa", "#f44336"),
            ("Xóa form", "#607D8B")
        ]
        
        for text, color in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    padding: 8px 15px;
                    background-color: {color};
                    color: white;
                    border-radius: 4px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {color}dd;
                }}
            """)
            button_layout.addWidget(btn)
            
            if text == "Thêm":
                btn.clicked.connect(self.addProduct)
            elif text == "Sửa":
                btn.clicked.connect(self.editProduct)
            elif text == "Xóa":
                btn.clicked.connect(self.deleteProduct)
            else:
                btn.clicked.connect(self.clearForm)
        
        left_panel.addLayout(button_layout)
        
        # Panel bên phải cho hình ảnh
        right_panel = QVBoxLayout()
        
        # Nút để toggle hiển thị phần hình ảnh
        self.toggle_image_button = QPushButton("Hiển thị phần hình ảnh")
        self.toggle_image_button.clicked.connect(self.toggleImageSection)
        self.toggle_image_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        right_panel.addWidget(self.toggle_image_button)
        
        # Container cho phần hình ảnh
        self.image_container = QWidget()
        image_layout = QVBoxLayout(self.image_container)
        
        # Khu vực hiển thị hình ảnh
        self.image_preview = QLabel("Chưa có hình ảnh")
        self.image_preview.setFixedSize(300, 300)  # Kích thước cố định
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                border-radius: 5px;
                background-color: #f5f5f5;
            }
        """)
        image_layout.addWidget(self.image_preview)
        
        # Nút chọn ảnh
        upload_button = QPushButton("Chọn Ảnh...")
        upload_button.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        upload_button.clicked.connect(self.selectImage)
        image_layout.addWidget(upload_button)
        
        self.image_container.setVisible(False)
        right_panel.addWidget(self.image_container)
        right_panel.addStretch()
        
        # Thêm các panel vào container
        form_container.addLayout(left_panel)
        form_container.addLayout(right_panel)
        main_layout.addLayout(form_container)

        # Thanh công cụ (tìm kiếm và xuất Excel)
        tools_layout = QHBoxLayout()
        
        # Nút xuất Excel
        export_button = QPushButton("Xuất Excel")
        export_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #217346;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1e6b3e;
            }
        """)
        export_button.clicked.connect(self.exportToExcel)
        tools_layout.addWidget(export_button)
        
        # Thanh tìm kiếm
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập mã hoặc tên sản phẩm...")
        self.search_input.setStyleSheet(input_style)
        
        self.search_button = QPushButton("Tìm kiếm")
        self.search_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.search_button.clicked.connect(self.searchProducts)
        
        tools_layout.addWidget(self.search_input)
        tools_layout.addWidget(self.search_button)
        main_layout.addLayout(tools_layout)
        
        # Bảng sản phẩm
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(
            ["Mã SP", "Tên SP", "Giá", "Tồn Kho", "Hình Ảnh", "Ngày Nhập"]
        )
        
        # Style cho bảng
        self.product_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        # Cấu hình bảng
        self.product_table.horizontalHeader().setStretchLastSection(True)
        self.product_table.setMinimumHeight(300)
        main_layout.addWidget(self.product_table)
        
        # Set main container as the scroll area widget
        main_scroll.setWidget(main_container)
        
        # Set the scroll area as the main widget's layout
        main_widget_layout = QVBoxLayout(self)
        main_widget_layout.addWidget(main_scroll)
        
        # Kết nối sự kiện chọn dòng trong bảng
        self.product_table.itemClicked.connect(self.tableItemClicked)

    def loadProducts(self):
        if not self.cursor:
            return
            
        try:
            self.cursor.execute("SELECT id, name, price, stock, image_path, import_date FROM products")
            products = self.cursor.fetchall()
            
            self.product_table.setRowCount(len(products))
            for i, product in enumerate(products):
                for j, value in enumerate(product):
                    if j == 4:  # Cột hình ảnh
                        if value and os.path.exists(value):
                            # Tạo QLabel để hiển thị hình ảnh
                            image_label = QLabel()
                            pixmap = QPixmap(value)
                            scaled_pixmap = pixmap.scaled(
                                75, 75,  # Kích thước thumbnail trong bảng
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation
                            )
                            image_label.setPixmap(scaled_pixmap)
                            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.product_table.setCellWidget(i, j, image_label)
                        else:
                            self.product_table.setItem(i, j, QTableWidgetItem("Không có ảnh"))
                    elif j == 5 and value:  # Định dạng ngày nhập
                        formatted_date = value.strftime("%d/%m/%Y")
                        self.product_table.setItem(i, j, QTableWidgetItem(formatted_date))
                    else:
                        self.product_table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
                        
            # Tự động điều chỉnh kích thước cột
            self.product_table.resizeColumnsToContents()
        except Exception as err:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu: {str(err)}")

    # All other methods remain the same
    def connectDB(self):
        self.conn = connect_db()
        if self.conn is None:
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối database!")
            return
        self.cursor = self.conn.cursor()

    def selectImage(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Chọn Hình Ảnh", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            self.selected_image_path = file_path
            self.displayImage(file_path)

    def displayImage(self, image_path):
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                300, 300,  # Fixed size
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_preview.setPixmap(scaled_pixmap)
        else:
            self.image_preview.setText("Chưa có hình ảnh")

    def toggleImageSection(self):
        self.is_image_section_visible = not self.is_image_section_visible
        self.image_container.setVisible(self.is_image_section_visible)
        self.toggle_image_button.setText(
            "Ẩn phần hình ảnh" if self.is_image_section_visible else "Hiển thị phần hình ảnh"
        )

    def saveImage(self, product_id):
        if not self.selected_image_path:
            return None
            
        _, ext = os.path.splitext(self.selected_image_path)
        new_filename = f"{product_id}{ext}"
        destination = os.path.join(self.image_folder, new_filename)
        
        try:
            shutil.copy2(self.selected_image_path, destination)
            return destination
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu hình ảnh: {str(e)}")
            return None

    def searchProducts(self):
        if not self.cursor:
            return
            
        keyword = self.search_input.text().strip()
        try:
            self.cursor.execute("""
                SELECT id, name, price, stock, image_path, import_date 
                FROM products 
                WHERE id LIKE %s OR name LIKE %s
            """, (f"%{keyword}%", f"%{keyword}%"))
            products = self.cursor.fetchall()
            
            self.product_table.setRowCount(len(products))
            for i, product in enumerate(products):
                for j, value in enumerate(product):
                    if j == 4:  # Cột hình ảnh
                        if value and os.path.exists(value):
                            image_label = QLabel()
                            pixmap = QPixmap(value)
                            scaled_pixmap = pixmap.scaled(
                                50, 50,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation
                            )
                            image_label.setPixmap(scaled_pixmap)
                            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.product_table.setCellWidget(i, j, image_label)
                        else:
                            self.product_table.setItem(i, j, QTableWidgetItem("Không có ảnh"))
                    elif j == 5 and value:  # Định dạng ngày nhập
                        formatted_date = value.strftime("%d/%m/%Y")
                        self.product_table.setItem(i, j, QTableWidgetItem(formatted_date))
                    else:
                        self.product_table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ""))
            
            self.product_table.resizeColumnsToContents()
        except Exception as err:
            QMessageBox.warning(self, "Lỗi", f"Lỗi tìm kiếm: {str(err)}")

    def exportToExcel(self):
        try:
            data = []
            headers = []
            for j in range(self.product_table.columnCount()):
                headers.append(self.product_table.horizontalHeaderItem(j).text())
            
            for i in range(self.product_table.rowCount()):
                row_data = []
                for j in range(self.product_table.columnCount()):
                    if j == 4:  # Cột hình ảnh
                        cell_widget = self.product_table.cellWidget(i, j)
                        if isinstance(cell_widget, QLabel) and cell_widget.pixmap():
                            row_data.append("Có hình ảnh")
                        else:
                            row_data.append("Không có ảnh")
                    else:
                        item = self.product_table.item(i, j)
                        row_data.append(item.text() if item else "")
                data.append(row_data)
            
            df = pd.DataFrame(data, columns=headers)
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Lưu File Excel", "", "Excel Files (*.xlsx)"
            )
            
            if file_path:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Thành công", "Xuất file Excel thành công!")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xuất file Excel: {str(e)}")

    def addProduct(self):
        if not self.cursor:
            return
            
        try:
            product_id = self.id_input.text().strip()
            name = self.name_input.text().strip()
            
            if not product_id or not name:
                QMessageBox.warning(self, "Lỗi", "Mã và tên sản phẩm không được để trống!")
                return
                
            try:
                price = float(self.price_input.text())
                if price < 0:
                    raise ValueError("Giá không được âm")
            except ValueError:
                QMessageBox.warning(self, "Lỗi", "Giá không hợp lệ!")
                return
                
            try:
                stock = int(self.stock_input.text())
                if stock < 0:
                    raise ValueError("Tồn kho không được âm")
            except ValueError:
                QMessageBox.warning(self, "Lỗi", "Tồn kho không hợp lệ!")
                return
                
            import_date = self.import_date.date().toString("yyyy-MM-dd")
            
            image_path = self.saveImage(product_id)
            
            self.cursor.execute("""
                INSERT INTO products (id, name, price, stock, image_path, import_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (product_id, name, price, stock, image_path, import_date))
            self.conn.commit()
            
            QMessageBox.information(self, "Thành công", "Thêm sản phẩm thành công!")
            self.loadProducts()
            self.clearForm()
        except Exception as err:
            QMessageBox.warning(self, "Lỗi", f"Không thể thêm sản phẩm: {str(err)}")

    def editProduct(self):
        if not self.cursor:
            return
            
        try:
            product_id = self.id_input.text().strip()
            name = self.name_input.text().strip()
            
            if not product_id or not name:
                QMessageBox.warning(self, "Lỗi", "Mã và tên sản phẩm không được để trống!")
                return
                
            try:
                price = float(self.price_input.text())
                if price < 0:
                    raise ValueError("Giá không được âm")
            except ValueError:
                QMessageBox.warning(self, "Lỗi", "Giá không hợp lệ!")
                return
                
            try:
                stock = int(self.stock_input.text())
                if stock < 0:
                    raise ValueError("Tồn kho không được âm")
            except ValueError:
                QMessageBox.warning(self, "Lỗi", "Tồn kho không hợp lệ!")
                return
                
            import_date = self.import_date.date().toString("yyyy-MM-dd")
            
            if self.selected_image_path:
                image_path = self.saveImage(product_id)
                
                self.cursor.execute("""
                    UPDATE products 
                    SET name = %s, price = %s, stock = %s, image_path = %s, import_date = %s
                    WHERE id = %s
                """, (name, price, stock, image_path, import_date, product_id))
            else:
                self.cursor.execute("""
                    UPDATE products 
                    SET name = %s, price = %s, stock = %s, import_date = %s
                    WHERE id = %s
                """, (name, price, stock, import_date, product_id))
                
            self.conn.commit()
            
            QMessageBox.information(self, "Thành công", "Cập nhật sản phẩm thành công!")
            self.loadProducts()
            self.clearForm()
        except Exception as err:
            QMessageBox.warning(self, "Lỗi", f"Không thể cập nhật sản phẩm: {str(err)}")

    def deleteProduct(self):
        if not self.cursor:
            return
        
        try:
            product_id = self.id_input.text().strip()
        
            if not product_id:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn sản phẩm để xóa!")
                return
            
            reply = QMessageBox.question(self, "Xác nhận", 
                "Bạn có chắc muốn xóa sản phẩm này? Việc này sẽ xóa cả thông tin đơn hàng liên quan.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                # Xóa các bản ghi liên quan trong order_items trước
                self.cursor.execute("DELETE FROM order_items WHERE product_id = %s", (product_id,))
            
                # Sau đó xóa sản phẩm
                self.cursor.execute("SELECT image_path FROM products WHERE id = %s", (product_id,))
                result = self.cursor.fetchone()
            
                if result and result[0] and os.path.exists(result[0]):
                    try:
                        os.remove(result[0])
                    except:
                        pass
            
                self.cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                self.conn.commit()
            
                QMessageBox.information(self, "Thành công", "Xóa sản phẩm thành công!")
                self.loadProducts()
                self.clearForm()
        except Exception as err:
            QMessageBox.warning(self, "Lỗi", f"Không thể xóa sản phẩm: {str(err)}")

    def tableItemClicked(self):
        current_row = self.product_table.currentRow()
        if current_row < 0:
            return
            
        self.id_input.setText(self.product_table.item(current_row, 0).text())
        self.name_input.setText(self.product_table.item(current_row, 1).text())
        self.price_input.setText(self.product_table.item(current_row, 2).text())
        self.stock_input.setText(self.product_table.item(current_row, 3).text())
        
        # Get image path and display image
        image_widget = self.product_table.cellWidget(current_row, 4)
        if isinstance(image_widget, QLabel) and image_widget.pixmap():
            self.cursor.execute("SELECT image_path FROM products WHERE id = %s", 
                              (self.product_table.item(current_row, 0).text(),))
            result = self.cursor.fetchone()
            if result and result[0]:
                self.displayImage(result[0])
                if not self.is_image_section_visible:
                    self.toggleImageSection()
        else:
            self.image_preview.setText("Chưa có hình ảnh")
        
        self.selected_image_path = None
        
        date_text = self.product_table.item(current_row, 5).text()
        if date_text:
            try:
                day, month, year = map(int, date_text.split('/'))
                self.import_date.setDate(QDate(year, month, day))
            except:
                self.import_date.setDate(QDate.currentDate())
        else:
            self.import_date.setDate(QDate.currentDate())

    def clearForm(self):
        self.id_input.clear()
        self.name_input.clear()
        self.price_input.clear()
        self.stock_input.clear()
        self.image_preview.setText("Chưa có hình ảnh")
        self.selected_image_path = None
        self.import_date.setDate(QDate.currentDate())