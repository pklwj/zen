import os
import sys
import tempfile
import img2pdf
from PIL import Image
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt

class DragDropPdfApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_folders = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Win11 拖拽多文件夹转 PDF 工具（支持透明PNG）")
        self.resize(550, 350)
        self.setAcceptDrops(True)
        
        main_layout = QVBoxLayout()

        # 1. 拖拽提示区域
        self.tip_label = QLabel("【请把想要转换的多个文件夹，直接拖入本窗口中】")
        self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tip_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background-color: #fafafa;
                font-size: 14px;
                font-weight: bold;
                color: #555;
                padding: 20px;
            }
        """)
        main_layout.addWidget(self.tip_label)

        main_layout.addWidget(QLabel("已拖入的文件夹列表:"))
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setPlaceholderText("等待拖入文件夹...")
        main_layout.addWidget(self.log_viewer)

        # 2. 输出目录选择部分
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("PDF 保存目录:"))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        hbox.addWidget(self.output_edit)
        btn_select_out = QPushButton("浏览目录...")
        btn_select_out.clicked.connect(self.select_output_dir)
        hbox.addWidget(btn_select_out)
        main_layout.addLayout(hbox)

        # 3. 开始转换按钮
        self.btn_convert = QPushButton("开始批量转换 (按原文件夹名命名)")
        self.btn_convert.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; font-size: 14px; padding: 10px;")
        self.btn_convert.clicked.connect(self.batch_convert)
        main_layout.addWidget(self.btn_convert)

        self.setLayout(main_layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        new_folders = []
        for url in urls:
            path = url.toLocalFile()
            if os.path.isdir(path) and path not in self.selected_folders:
                new_folders.append(path)
        if new_folders:
            self.selected_folders.extend(new_folders)
            self.log_viewer.clear()
            self.log_viewer.append("\n".join(self.selected_folders))
            self.tip_label.setText(f"已成功捕获 {len(self.selected_folders)} 个文件夹")
            self.tip_label.setStyleSheet("border: 2px dashed #4CAF50; background-color: #e8f5e9; font-size: 14px; font-weight: bold; color: green; padding: 20px;")

    def select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择生成的 PDF 存放目录")
        if directory:
            self.output_edit.setText(directory)

    def process_image_alpha(self, img_path, temp_dir):
        """
        检查图片是否有 Alpha 通道，如果有则将其转换为白底并保存到临时目录
        """
        try:
            with Image.open(img_path) as img:
                # 检查模式是否为 RGBA 或包含 transparency 属性
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    # 创建一个纯白背景画布
                    alpha_removed_img = Image.new("RGB", img.size, (255, 255, 255))
                    # 将原图粘贴到白底上，使用原图的 alpha 通道作为掩码
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    alpha_removed_img.paste(img, mask=img.split()[-1])
                    
                    # 生成临时文件路径
                    base_name = os.path.splitext(os.path.basename(img_path))[0]
                    temp_path = os.path.join(temp_dir, f"{base_name}_no_alpha.jpg")
                    alpha_removed_img.save(temp_path, "JPEG", quality=95)
                    return temp_path
        except Exception:
            pass
        return img_path

    def batch_convert(self):
        out_dir = self.output_edit.text()
        if not self.selected_folders:
            QMessageBox.warning(self, "警告", "请先拖入至少一个图片文件夹！")
            return
        if not out_dir:
            QMessageBox.warning(self, "警告", "请先选择 PDF 的保存目录！")
            return

        valid_extensions = ('.jpg', '.jpeg', '.png')
        success_count = 0
        error_logs = []

        self.btn_convert.setText("批量转换中...")
        self.btn_convert.setEnabled(False)
        QApplication.processEvents()

        # 使用 Python 的临时目录，转换完成后自动清理中间文件
        with tempfile.TemporaryDirectory() as temp_dir:
            for folder_path in self.selected_folders:
                folder_name = os.path.basename(os.path.normpath(folder_path))
                target_pdf_path = os.path.join(out_dir, f"{folder_name}.pdf")

                try:
                    raw_images = [
                        os.path.join(folder_path, f) 
                        for f in os.listdir(folder_path) 
                        if f.lower().endswith(valid_extensions)
                    ]
                    raw_images.sort()

                    if not raw_images:
                        error_logs.append(f"【{folder_name}】未找到符合要求的图片(JPG/PNG)")
                        continue

                    # 核心修复逻辑：对所有图片进行透明通道预处理
                    final_image_paths = []
                    for img_p in raw_images:
                        processed_p = self.process_image_alpha(img_p, temp_dir)
                        final_image_paths.append(processed_p)

                    # 写入 PDF
                    with open(target_pdf_path, "wb") as f:
                        f.write(img2pdf.convert(final_image_paths))
                    success_count += 1

                except Exception as e:
                    error_logs.append(f"【{folder_name}】转换失败: {str(e)}")

        self.btn_convert.setText("开始批量转换 (按原文件夹名命名)")
        self.btn_convert.setEnabled(True)

        if error_logs:
            error_msg = "\n".join(error_logs)
            QMessageBox.information(self, "转换完成", f"成功转换 {success_count} 个文件夹。\n\n部分文件夹存在问题:\n{error_msg}")
        else:
            QMessageBox.information(self, "成功", f"所有文件夹批量转换成功！\n共生成 {success_count} 个 PDF 文件。\n保存路径：{out_dir}")
        
        self.selected_folders = []
        self.log_viewer.clear()
        self.tip_label.setText("【请把想要转换的多个文件夹，直接拖入本窗口中】")
        self.tip_label.setStyleSheet("border: 2px dashed #aaa; background-color: #fafafa; font-size: 14px; font-weight: bold; color: #555; padding: 20px;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DragDropPdfApp()
    ex.show()
    sys.exit(app.exec())