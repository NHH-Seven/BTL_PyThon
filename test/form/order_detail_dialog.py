from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTableWidget, 
                              QPushButton, QHBoxLayout, QTableWidgetItem, QHeaderView,
                              QMessageBox, QWidget, QGridLayout, QFileDialog)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from database_connection import connect_db
from datetime import datetime
import tempfile
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from form.edit_order_dialog import EditOrderDialog
import globals  # Import globals to access current_user_id

class OrderDetailDialog(QDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        self.parent = parent  # Store parent reference for refreshing the table later
        self.setWindowTitle(f"Chi tiết đơn hàng #{order_id}")
        self.setMinimumSize(600, 400)
        
        # Get current user's role for permission checking
        self.current_user_role = self.getCurrentUserRole()
        
        self.initUI()
        self.loadOrderDetails()
        
    def getCurrentUserRole(self):
        """Get the current user's role from the database using globals.current_user_id"""
        conn = connect_db()
        user_role = "User"  # Default role if lookup fails
        
        if conn and globals.current_user_id:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT role FROM users WHERE id = %s", (globals.current_user_id,))
                result = cursor.fetchone()
                if result:
                    user_role = result[0]
            except Exception as e:
                print(f"Error fetching user role: {str(e)}")
            finally:
                conn.close()
                
        return user_role
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Order information section
        info_container = QWidget()
        info_container.setStyleSheet("""
            background-color: #E3F2FD;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
        """)
        info_layout = QGridLayout(info_container)
        
        # Info labels
        self.id_label = QLabel(f"Mã đơn hàng: #{self.order_id}")
        self.id_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        self.customer_label = QLabel("Khách hàng: ")
        self.phone_label = QLabel("Số điện thoại: ")
        self.date_label = QLabel("Ngày đặt: ")
        self.status_label = QLabel("Phương thức thanh toán: ")
        self.total_label = QLabel("Tổng tiền: ")
        self.total_label.setStyleSheet("color: #d35400; font-weight: bold;")
        
        info_layout.addWidget(self.id_label, 0, 0, 1, 2)
        info_layout.addWidget(self.customer_label, 1, 0)
        info_layout.addWidget(self.phone_label, 1, 1)
        info_layout.addWidget(self.date_label, 2, 0)
        info_layout.addWidget(self.status_label, 2, 1)
        info_layout.addWidget(self.total_label, 3, 0, 1, 2)
        
        layout.addWidget(info_container)
        
        # Order items table
        items_label = QLabel("Sản phẩm trong đơn hàng:")
        items_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(items_label)
        
        self.items_table = QTableWidget(0, 5)
        self.items_table.setHorizontalHeaderLabels([
            "Mã SP", "Tên sản phẩm", "Đơn giá", "Số lượng", "Thành tiền"
        ])
        
        # Adjust column widths
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Price
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Quantity
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Total
        
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
        
        # Button container for all buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        
        # Edit button
        self.edit_button = QPushButton("Sửa")
        self.edit_button.setStyleSheet("""
            background-color: #FFA000;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        self.edit_button.clicked.connect(self.editOrder)
        
        # Delete button
        self.delete_button = QPushButton("Xóa")
        self.delete_button.setStyleSheet("""
            background-color: #F44336;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        self.delete_button.clicked.connect(self.deleteOrder)
        
        # Export PDF button
        export_button = QPushButton("Xuất hóa đơn PDF")
        export_button.setStyleSheet("""
            background-color: #009688;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        export_button.clicked.connect(self.exportToPDF)
        
        # Close button
        close_button = QPushButton("Đóng")
        close_button.setStyleSheet("""
            background-color: #1976D2;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        """)
        close_button.clicked.connect(self.accept)
        
        # Add all buttons to layout with some space
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(export_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        # Disable edit/delete buttons if user is not admin
        if self.current_user_role.lower() != "admin":
            # We could disable them, but we'll leave them enabled and check permissions when clicked
            # This provides better UX by showing an informative message instead of just greying them out
            # self.edit_button.setEnabled(False)
            # self.delete_button.setEnabled(False)
            
            # Optionally add a visual indicator that these buttons may require special permissions
            non_admin_button_style = """
                background-color: #9E9E9E;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            """
            self.edit_button.setStyleSheet(non_admin_button_style)
            self.delete_button.setStyleSheet(non_admin_button_style)
        
        layout.addWidget(button_container)
        
    def loadOrderDetails(self):
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
                
                # Format date
                date_obj = date
                if isinstance(date, str):
                    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                
                # Update labels
                self.customer_label.setText(f"Khách hàng: {customer_name}")
                self.phone_label.setText(f"Số điện thoại: {phone}")
                self.date_label.setText(f"Ngày đặt: {formatted_date}")
                self.status_label.setText(f"Phương thức thanh toán: {status}")
                self.total_label.setText(f"Tổng tiền: {format(total, ',.0f')} VNĐ")
                
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
                    quantity_item = QTableWidgetItem(str(quantity))
                    total_item = QTableWidgetItem(f"{format(item_total, ',.0f')} VNĐ")
                    
                    # Set alignment
                    id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    quantity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    
                    # Set items to table
                    self.items_table.setItem(row_idx, 0, id_item)
                    self.items_table.setItem(row_idx, 1, name_item)
                    self.items_table.setItem(row_idx, 2, price_item)
                    self.items_table.setItem(row_idx, 3, quantity_item)
                    self.items_table.setItem(row_idx, 4, total_item)
                
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể tải chi tiết đơn hàng: {str(e)}")
            finally:
                conn.close()
                
    def checkAdminPermission(self):
        """Check if current user has admin permissions"""
        if self.current_user_role.lower() != "admin":
            QMessageBox.warning(
                self, 
                "Không có quyền", 
                "Bạn không có quyền thực hiện chức năng này.\nChỉ quản trị viên (Admin) mới có thể sửa hoặc xóa đơn hàng."
            )
            return False
        return True
                
    # Implement edit function with permission check
    def editOrder(self):
        # Check permissions first
        if not self.checkAdminPermission():
            return
            
        # If user has permissions, proceed with edit
        edit_dialog = EditOrderDialog(self.order_id, self)
        edit_dialog.exec()
        
    # Implement delete function with permission check
    def deleteOrder(self):
        # Check permissions first
        if not self.checkAdminPermission():
            return
            
        # If user has permissions, proceed with delete
        reply = QMessageBox.question(self, "Xác nhận xóa", 
                                    f"Bạn có chắc chắn muốn xóa đơn hàng #{self.order_id}?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            conn = connect_db()
            if conn:
                try:
                    cursor = conn.cursor()
                    
                    # First delete order items (foreign key constraint)
                    cursor.execute("DELETE FROM order_items WHERE order_id = %s", (self.order_id,))
                    
                    # Then delete the order
                    cursor.execute("DELETE FROM orders WHERE id = %s", (self.order_id,))
                    
                    # Commit the transaction
                    conn.commit()
                    
                    QMessageBox.information(self, "Thành công", 
                                           f"Đã xóa đơn hàng #{self.order_id}")
                    
                    # Refresh the order list in parent widget
                    if self.parent and hasattr(self.parent, 'refreshAfterPayment'):
                        self.parent.refreshAfterPayment()
                    
                    # Close dialog
                    self.accept()
                    
                except Exception as e:
                    conn.rollback()
                    QMessageBox.warning(self, "Lỗi", f"Không thể xóa đơn hàng: {str(e)}")
                finally:
                    conn.close()
    
    # Implement PDF export function (no permission check needed - all users can export PDF)
    def exportToPDF(self):
        try:
            # Get order information
            conn = connect_db()
            if not conn:
                QMessageBox.warning(self, "Lỗi", "Không thể kết nối tới cơ sở dữ liệu!")
                return
                
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
                conn.close()
                return
            
            customer_name, phone, date, status, total = order_info
            
            # Format date
            date_obj = date
            if isinstance(date, str):
                date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
            
            # Get order items
            cursor.execute("""
                SELECT p.name, oi.price, oi.quantity, (oi.price * oi.quantity) as item_total
                FROM order_items oi
                JOIN products p ON p.id = oi.product_id
                WHERE oi.order_id = %s
            """, (self.order_id,))
            
            items = cursor.fetchall()
            conn.close()
            
            # Create PDF file
            # Ask for save location
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Lưu hóa đơn", 
                f"hoa_don_{self.order_id}.pdf", 
                "PDF Files (*.pdf)"
            )
            
            if not file_name:
                return  # User canceled
                
            # Create PDF
            doc = SimpleDocTemplate(
                file_name, 
                pagesize=A4,
                rightMargin=72, 
                leftMargin=72,
                topMargin=72, 
                bottomMargin=72
            )
            
            # Register a Unicode font that supports Vietnamese characters
            # Note: For Vietnamese support, you need to ensure appropriate fonts are available
            # For this example, we'll assume the system has Arial Unicode MS
            try:
                pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
            except:
                # Fallback to default font if Arial.ttf is not available
                pass
                
            # Create styles
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Center', alignment=1))
            styles.add(ParagraphStyle(
                name='VietnameseNormal',
                fontName='Arial',
                fontSize=12
            ))
            styles.add(ParagraphStyle(
                name='VietnameseTitle',
                fontName='Arial',
                fontSize=16,
                alignment=1,
                spaceAfter=12
            ))
            
            # Build PDF content
            elements = []
            
            # Title
            elements.append(Paragraph("HÓA ĐƠN Vippro Coffee", styles['VietnameseTitle']))
            elements.append(Spacer(1, 12))
            
            # Shop information
            elements.append(Paragraph("CỬA HÀNG: [Coffee Shop]", styles['VietnameseNormal']))
            elements.append(Paragraph("Địa chỉ: [Phú Diễn, Bắc Từ Liên, Hà Nội]", styles['VietnameseNormal']))
            elements.append(Paragraph("Điện thoại: [0336759385", styles['VietnameseNormal']))
            elements.append(Spacer(1, 12))
            
            # Order information
            elements.append(Paragraph(f"Mã đơn hàng: #{self.order_id}", styles['VietnameseNormal']))
            elements.append(Paragraph(f"Ngày: {formatted_date}", styles['VietnameseNormal']))
            elements.append(Paragraph(f"Khách hàng: {customer_name}", styles['VietnameseNormal']))
            elements.append(Paragraph(f"Số điện thoại: {phone}", styles['VietnameseNormal']))
            elements.append(Paragraph(f"Phương thức thanh toán: {status}", styles['VietnameseNormal']))
            elements.append(Spacer(1, 12))
            
            # Items table
            table_data = [['STT', 'Tên sản phẩm', 'Đơn giá', 'Số lượng', 'Thành tiền']]
            
            for idx, item in enumerate(items, 1):
                name, price, quantity, item_total = item
                table_data.append([
                    str(idx),
                    name,
                    f"{format(price, ',.0f')} VNĐ",
                    str(quantity),
                    f"{format(item_total, ',.0f')} VNĐ"
                ])
            
            # Add total row
            table_data.append(['', '', '', 'Tổng cộng:', f"{format(total, ',.0f')} VNĐ"])
            
            # Create the table
            table = Table(table_data, colWidths=[30, 200, 100, 60, 100])
            
            # Style the table
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Arial'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # First column centered
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),   # Price column right aligned
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Quantity column centered
                ('ALIGN', (4, 1), (4, -1), 'RIGHT'),   # Total column right aligned
                ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -2), 1, colors.black),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
                ('ALIGN', (3, -1), (3, -1), 'RIGHT'),  # "Total:" label right aligned
                ('ALIGN', (4, -1), (4, -1), 'RIGHT'),  # Total amount right aligned
                ('FONTNAME', (3, -1), (4, -1), 'Arial'),
                ('FONTSIZE', (3, -1), (4, -1), 12),
                ('BOLD', (3, -1), (4, -1), 1),
            ])
            
            table.setStyle(table_style)
            elements.append(table)
            elements.append(Spacer(1, 12))
            
            # Footer - terms and signature
            elements.append(Paragraph("Thank kiu quý khách đã mua hàng của chúng tôi!\n Chúc quý khách một ngày vui vẻ. ", styles['VietnameseNormal']))
            elements.append(Spacer(1, 30))
            
            
            
            # Build the PDF
            doc.build(elements)
            
            QMessageBox.information(self, "Thành công", 
                                 f"Đã xuất hóa đơn PDF thành công!\nFile: {file_name}")
            
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xuất hóa đơn PDF: {str(e)}")