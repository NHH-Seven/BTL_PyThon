from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QLineEdit, 
                             QPushButton, QHBoxLayout, QFormLayout, QMessageBox, 
                             QTableWidgetItem, QDialog, QComboBox, QSpinBox, 
                             QCalendarWidget, QTabWidget, QGridLayout, QFrame,
                             QApplication, QSplitter)
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtCore import Qt, QDate, QSize
from database_connection import connect_db
import sys

class EmployeeDialog(QDialog):
    def __init__(self, parent=None, employee_data=None):
        super().__init__(parent)
        self.setWindowTitle("Thông tin nhân viên")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.connectDB()
        
        layout = QVBoxLayout(self)
        
        # Tạo frame chứa form
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        form_frame.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 10px; }")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Tạo các trường nhập liệu với style
        self.id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        self.position_input = QComboBox()
        self.position_input.addItems(["Nhân viên pha chế", "Nhân viên phục vụ", "Thu ngân", "Quản lý"])
        self.salary_input = QSpinBox()
        self.salary_input.setRange(0, 50000000)
        self.salary_input.setSingleStep(500000)
        self.salary_input.setSuffix(" VNĐ")
        self.start_date = QCalendarWidget()
        
        # Style cho các input
        input_style = """
            QLineEdit, QComboBox, QSpinBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """
        self.id_input.setStyleSheet(input_style)
        self.name_input.setStyleSheet(input_style)
        self.phone_input.setStyleSheet(input_style)
        self.address_input.setStyleSheet(input_style)
        self.position_input.setStyleSheet(input_style)
        self.salary_input.setStyleSheet(input_style)
        
        # Thêm các trường vào form
        form_layout.addRow("Mã nhân viên:", self.id_input)
        form_layout.addRow("Tên nhân viên:", self.name_input)
        form_layout.addRow("Số điện thoại:", self.phone_input)
        form_layout.addRow("Địa chỉ:", self.address_input)
        form_layout.addRow("Chức vụ:", self.position_input)
        form_layout.addRow("Lương cơ bản:", self.salary_input)
        form_layout.addRow("Ngày bắt đầu:", self.start_date)
        
        layout.addWidget(form_frame)
        
        # Nếu có dữ liệu nhân viên, điền vào form
        if employee_data:
            self.id_input.setText(employee_data[0])
            self.name_input.setText(employee_data[1])
            self.phone_input.setText(employee_data[2])
            self.address_input.setText(employee_data[3])
            self.position_input.setCurrentText(employee_data[4])
            # Xử lý lương từ chuỗi định dạng thành số
            salary_str = employee_data[5].replace(" VNĐ", "").replace(",", "")
            self.salary_input.setValue(int(salary_str))
            
            # Xử lý ngày tháng
            date_parts = employee_data[6].split('/')
            date = QDate(int(date_parts[2]), int(date_parts[1]), int(date_parts[0]))
            self.start_date.setSelectedDate(date)
            
            self.id_input.setReadOnly(True)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.confirm_button = QPushButton("Xác nhận")
        self.cancel_button = QPushButton("Hủy")
        
        button_style = """
            QPushButton {
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton#confirm {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#cancel {
                background-color: #f44336;
                color: white;
            }
        """
        self.confirm_button.setObjectName("confirm")
        self.cancel_button.setObjectName("cancel")
        self.confirm_button.setStyleSheet(button_style)
        self.cancel_button.setStyleSheet(button_style)
        
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def connectDB(self):
        self.conn = connect_db()
        if self.conn is None:
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối database!")
            return
        self.cursor = self.conn.cursor()

    def get_employee_data(self):
        return [
            self.id_input.text(),
            self.name_input.text(),
            self.phone_input.text(),
            self.address_input.text(),
            self.position_input.currentText(),
            f"{self.salary_input.value():,} VNĐ",
            self.start_date.selectedDate().toString("dd/MM/yyyy")
        ]

class EmployeeManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        self.connectDB()
        self.load_employees()
        
    def connectDB(self):
        self.conn = connect_db()
        if self.conn is None:
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối database!")
            return False
        self.cursor = self.conn.cursor()
        return True

    def load_employees(self):
        if not hasattr(self, 'conn') or self.conn is None:
            if not self.connectDB():
                return
            
        # Xóa dữ liệu cũ trong bảng
        self.employee_table.setRowCount(0)
    
        try:
            # Truy vấn tất cả nhân viên
            self.cursor.execute("SELECT employee_id, name, phone, address, position, salary, DATE_FORMAT(start_date, '%d/%m/%Y') FROM employees")

            employees = self.cursor.fetchall()
        
            # Đổ dữ liệu vào table
            for row_data in employees:
                row = self.employee_table.rowCount()
                self.employee_table.insertRow(row)
                for col, value in enumerate(row_data):
                    if col == 5:  # Cột lương
                        formatted_salary = f"{value:,} VNĐ"
                        item = QTableWidgetItem(formatted_salary)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    else:
                        item = QTableWidgetItem(str(value))
                    self.employee_table.setItem(row, col, item)
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách nhân viên: {str(e)}")
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Quản Lý Nhân Viên - Coffee Shop")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        main_layout.addLayout(header_layout)
        
        # Search bar and action buttons in one frame
        control_frame = QFrame()
        control_frame.setFrameShape(QFrame.Shape.StyledPanel)
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        control_layout = QVBoxLayout(control_frame)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm nhân viên...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        
        self.search_button = QPushButton("Tìm kiếm")
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        self.reset_button = QPushButton("Hiển thị tất cả")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.reset_button)
        control_layout.addLayout(search_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Thêm nhân viên")
        self.edit_button = QPushButton("Sửa thông tin")
        self.delete_button = QPushButton("Xóa nhân viên")
        self.print_button = QPushButton("Xuất danh sách")
        
        button_style = """
            QPushButton {
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """
        self.add_button.setStyleSheet(button_style + "background-color: #4CAF50; color: white;")
        self.edit_button.setStyleSheet(button_style + "background-color: #FFC107; color: white;")
        self.delete_button.setStyleSheet(button_style + "background-color: #f44336; color: white;")
        self.print_button.setStyleSheet(button_style + "background-color: #2196F3; color: white;")
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.print_button)
        control_layout.addLayout(button_layout)
        
        main_layout.addWidget(control_frame)
        
        # Employee table
        self.employee_table = QTableWidget(0, 7)
        self.employee_table.setHorizontalHeaderLabels([
            "Mã NV", "Họ và tên", "Số điện thoại", 
            "Địa chỉ", "Chức vụ", "Lương cơ bản", "Ngày bắt đầu"
        ])
        self.employee_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        
        # Cài đặt chiều rộng các cột
        self.employee_table.setColumnWidth(0, 80)   # Mã NV
        self.employee_table.setColumnWidth(1, 200)  # Họ và tên
        self.employee_table.setColumnWidth(2, 130)  # SĐT
        self.employee_table.setColumnWidth(3, 250)  # Địa chỉ
        self.employee_table.setColumnWidth(4, 150)  # Chức vụ
        self.employee_table.setColumnWidth(5, 130)  # Lương
        self.employee_table.setColumnWidth(6, 130)  # Ngày bắt đầu
        
        self.employee_table.horizontalHeader().setStretchLastSection(True)
        self.employee_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.employee_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.employee_table.setAlternatingRowColors(True)
        self.employee_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                alternate-background-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        
        main_layout.addWidget(self.employee_table)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Sẵn sàng")
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout)

    def setup_connections(self):
        self.add_button.clicked.connect(self.add_employee)
        self.edit_button.clicked.connect(self.edit_employee)
        self.delete_button.clicked.connect(self.delete_employee)
        self.search_button.clicked.connect(self.search_employees)
        self.reset_button.clicked.connect(self.load_employees)
        self.print_button.clicked.connect(self.print_employee_list)
        self.employee_table.doubleClicked.connect(self.edit_employee)
        
    def add_employee(self):
        dialog = EmployeeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            employee_data = dialog.get_employee_data()
        
            # Kiểm tra kết nối
            if not hasattr(self, 'conn') or self.conn is None:
                if not self.connectDB():
                    return
                
            try:
                # Kiểm tra dữ liệu nhập vào
                if not employee_data[0] or not employee_data[1]:
                    QMessageBox.warning(self, "Cảnh báo", "Mã nhân viên và tên nhân viên không được để trống!")
                    return
                
                # Kiểm tra mã nhân viên đã tồn tại chưa
                self.cursor.execute("SELECT employee_id FROM employees WHERE employee_id = %s", (employee_data[0],))
                if self.cursor.fetchone():
                    QMessageBox.warning(self, "Cảnh báo", f"Mã nhân viên {employee_data[0]} đã tồn tại!")
                    return
                
                # Chuyển đổi định dạng ngày
                date_parts = employee_data[6].split('/')
                mysql_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
            
                # Chuyển đổi định dạng lương
                salary = int(employee_data[5].replace(" VNĐ", "").replace(",", ""))
            
                # Thêm nhân viên vào database
                query = """
                    INSERT INTO employees (employee_id, name, phone, address, position, salary, start_date) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(query, (
                    employee_data[0], employee_data[1], employee_data[2], 
                    employee_data[3], employee_data[4], salary, mysql_date
                ))
                self.conn.commit()
            
                # Tải lại danh sách nhân viên
                self.load_employees()
                self.status_label.setText(f"Đã thêm nhân viên {employee_data[1]} thành công!")
                QMessageBox.information(self, "Thành công", "Đã thêm nhân viên mới thành công!")
                
            except Exception as e:
                self.conn.rollback()
                QMessageBox.critical(self, "Lỗi", f"Không thể thêm nhân viên: {str(e)}")
            
    def edit_employee(self):
        current_row = self.employee_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn nhân viên cần sửa!")
            return
        
        # Lấy dữ liệu nhân viên hiện tại
        employee_data = []
        for col in range(self.employee_table.columnCount()):
            item = self.employee_table.item(current_row, col)
            employee_data.append(item.text())
        
        dialog = EmployeeDialog(self, employee_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_employee_data()
        
            # Kiểm tra kết nối
            if not hasattr(self, 'conn') or self.conn is None:
                if not self.connectDB():
                    return
                
            try:
                # Kiểm tra dữ liệu nhập vào
                if not new_data[1]:
                    QMessageBox.warning(self, "Cảnh báo", "Tên nhân viên không được để trống!")
                    return
                    
                # Chuyển đổi định dạng ngày
                date_parts = new_data[6].split('/')
                mysql_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
            
                # Chuyển đổi định dạng lương
                salary = int(new_data[5].replace(" VNĐ", "").replace(",", ""))
            
                # Cập nhật nhân viên trong database
                query = """
                    UPDATE employees 
                    SET name = %s, phone = %s, address = %s, position = %s, salary = %s, start_date = %s
                    WHERE employee_id = %s
                """
                self.cursor.execute(query, (
                    new_data[1], new_data[2], new_data[3], 
                    new_data[4], salary, mysql_date, new_data[0]
                ))
                self.conn.commit()
            
                # Tải lại danh sách nhân viên
                self.load_employees()
                self.status_label.setText(f"Đã cập nhật thông tin nhân viên {new_data[1]} thành công!")
                QMessageBox.information(self, "Thành công", "Đã cập nhật thông tin nhân viên thành công!")
                
            except Exception as e:
                self.conn.rollback()
                QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật thông tin nhân viên: {str(e)}")
            
    def delete_employee(self):
        current_row = self.employee_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn nhân viên cần xóa!")
            return
        
        employee_id = self.employee_table.item(current_row, 0).text()
        employee_name = self.employee_table.item(current_row, 1).text()
    
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa nhân viên {employee_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
    
        if reply == QMessageBox.StandardButton.Yes:
            # Kiểm tra kết nối
            if not hasattr(self, 'conn') or self.conn is None:
                if not self.connectDB():
                    return
                
            try:
                # Xóa nhân viên
                self.cursor.execute("DELETE FROM employees WHERE employee_id = %s", (employee_id,))
                self.conn.commit()
            
                # Tải lại danh sách nhân viên
                self.load_employees()
                self.status_label.setText(f"Đã xóa nhân viên {employee_name} thành công!")
                QMessageBox.information(self, "Thành công", "Đã xóa nhân viên thành công!")
                
            except Exception as e:
                self.conn.rollback()
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa nhân viên: {str(e)}")

    def search_employees(self):
        keyword = self.search_input.text().lower()
        if not keyword:
            self.load_employees()
            return
        
        # Kiểm tra kết nối
        if not hasattr(self, 'conn') or self.conn is None:
            if not self.connectDB():
                return
            
        try:
            # Tìm kiếm nhân viên trong database
            query = """
                SELECT employee_id, name, phone, address, position, salary, DATE_FORMAT(start_date, '%d/%m/%Y')
                FROM employees
                WHERE LOWER(employee_id) LIKE %s
                OR LOWER(name) LIKE %s
                OR LOWER(phone) LIKE %s
                OR LOWER(address) LIKE %s
                OR LOWER(position) LIKE %s
            """
            search_param = f"%{keyword}%"
            self.cursor.execute(query, (search_param, search_param, search_param, search_param, search_param))
            employees = self.cursor.fetchall()
        
            # Xóa dữ liệu cũ trong bảng
            self.employee_table.setRowCount(0)
        
            # Đổ dữ liệu vào table
            for row_data in employees:
                row = self.employee_table.rowCount()
                self.employee_table.insertRow(row)
                for col, value in enumerate(row_data):
                    if col == 5:  # Cột lương
                        formatted_salary = f"{value:,} VNĐ"
                        item = QTableWidgetItem(formatted_salary)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    else:
                        item = QTableWidgetItem(str(value))
                    self.employee_table.setItem(row, col, item)
            
            count = self.employee_table.rowCount()
            self.status_label.setText(f"Tìm thấy {count} nhân viên phù hợp với từ khóa '{keyword}'")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tìm kiếm nhân viên: {str(e)}")

    def print_employee_list(self):
        try:
            # Tạo nội dung báo cáo
            content = "DANH SÁCH NHÂN VIÊN COFFEE SHOP\n"
            content += "=" * 80 + "\n\n"
            
            from datetime import datetime
            current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            content += f"Ngày xuất: {current_time}\n\n"
            
            # Header
            headers = []
            for col in range(self.employee_table.columnCount()):
                headers.append(self.employee_table.horizontalHeaderItem(col).text())
            content += "\t".join(headers) + "\n"
            content += "-" * 80 + "\n"
            
            # Data
            for row in range(self.employee_table.rowCount()):
                if not self.employee_table.isRowHidden(row):
                    row_data = []
                    for col in range(self.employee_table.columnCount()):
                        item = self.employee_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    content += "\t".join(row_data) + "\n"
            
            # Thống kê
            total_employees = sum(1 for row in range(self.employee_table.rowCount()) 
                                if not self.employee_table.isRowHidden(row))
            content += f"\nTổng số nhân viên: {total_employees}\n"
            
            # Lưu file
            filename = f"employee_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.status_label.setText(f"Đã xuất danh sách nhân viên thành file: {filename}")
            QMessageBox.information(
                self,
                "Thành công",
                f"Đã xuất danh sách nhân viên thành công!\nFile: {filename}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Có lỗi xảy ra khi xuất danh sách: {str(e)}"
            )

# Giữ lại class EmployeeManagement cũ để đảm bảo khả năng tương thích với code cũ
class EmployeeManagement(EmployeeManagementTab):
    def __init__(self):
        super().__init__()

# Cho phép chạy module này như một ứng dụng độc lập
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Thiết lập style cho toàn bộ ứng dụng
    app.setStyle("Fusion")
    
    # Tạo cửa sổ chính
    window = QWidget()
    window.setWindowTitle("Quản lý nhân viên - Coffee Shop")
    layout = QVBoxLayout(window)
    
    # Thêm module quản lý nhân viên
    employee_tab = EmployeeManagementTab()
    layout.addWidget(employee_tab)
    
    window.setMinimumSize(1000, 600)
    window.show()
    
    sys.exit(app.exec())