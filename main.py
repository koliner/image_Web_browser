import sys
import os
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox

from index import Ui_MainWindow,get_resource_path
import image_operations
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("E2021140")



def pixmap_to_array(pixmap):
    """将 QPixmap 转换为 numpy 数组"""
    image = pixmap.toImage()
    image = image.convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
    width = image.width()
    height = image.height()
    ptr = image.bits()
    ptr.setsize(image.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)
    return arr

def array_to_pixmap(arr):
    """将 numpy 数组转换为 QPixmap"""
    height, width, channel = arr.shape
    bytes_per_line = 4 * width
    qimage = QtGui.QImage(arr.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_RGBA8888)
    return QtGui.QPixmap.fromImage(qimage)

class MainWindow(QtWidgets.QMainWindow):
    updateStatusBar = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 初始化变量
        self.current_image_path = None
        self.original_pixmap = None
        self.rotation_angle = 90
        self.tree_visible = False
        self.image_modified = False

        # 初始化UI
        self.initialize_ui()

        # 连接信号和槽
        self.connect_signals()

        # 为目录树启用上下文菜单
        self.ui.treeWidget_3.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.treeWidget_3.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """显示上下文菜单"""
        item = self.ui.treeWidget_3.itemAt(position)
        if item:
            file_path = item.data(0, QtCore.Qt.UserRole)
            if file_path and os.path.isfile(file_path):
                menu = QtWidgets.QMenu(self)

                # 添加显示图片信息的选项
                info_action = menu.addAction("显示图片信息")
                info_action.triggered.connect(lambda: self.show_image_info(file_path))

                # 添加重命名图片的选项
                rename_action = menu.addAction("重命名图片")
                rename_action.triggered.connect(lambda: self.rename_image(item, file_path))

                # 添加打开所在文件夹的选项
                open_folder_action = menu.addAction("打开所在文件夹")
                open_folder_action.triggered.connect(lambda: self.open_containing_folder(file_path))

                # 显示菜单
                menu.exec_(self.ui.treeWidget_3.viewport().mapToGlobal(position))

    def show_image_info(self, file_path):
        """显示图片信息"""
        image = QtGui.QImage(file_path)
        info = f"文件路径: {file_path}\n"
        info += f"宽度: {image.width()} 像素\n"
        info += f"高度: {image.height()} 像素\n"
        info += f"格式: {image.format()}\n"
        QMessageBox.information(self, "图片信息", info)

    def rename_image(self, item, file_path):
        """重命名图片"""
        dir_path = os.path.dirname(file_path)
        old_name = os.path.basename(file_path)
        new_name, ok = QtWidgets.QInputDialog.getText(self, "重命名图片", "输入新的文件名:", text=old_name)

        if ok and new_name:
            new_path = os.path.join(dir_path, new_name)
            if not os.path.exists(new_path):
                os.rename(file_path, new_path)
                item.setText(0, new_name)
                item.setData(0, QtCore.Qt.UserRole, new_path)
                QMessageBox.information(self, "重命名图片", "图片重命名成功！")
            else:
                QMessageBox.warning(self, "重命名图片", "目标文件名已存在，请选择其他名称。")

    def open_containing_folder(self, file_path):
        """打开图片所在文件夹"""
        dir_path = os.path.dirname(file_path)
        QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(dir_path))

    def initialize_ui(self):
        """初始化用户界面设置"""
        self.ui.menu_2.setEnabled(False)
        self.ui.action1_4.setEnabled(False)
        self.ui.action2_4.setEnabled(False)
        self.ui.action3_3.setEnabled(False)
        self.ui.action_6.setEnabled(False)
        # 创建一个 QLabel 来显示图像
        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setScaledContents(False)  # 不自动缩放内容

        # 创建 QScrollArea 并将 QLabel 添加到其中
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)

        # 将 QScrollArea 设置为中央小部件
        self.setCentralWidget(self.scroll_area)

        # 初始化工具栏按钮状态
        self.disable_toolbar_buttons()

    def connect_signals(self):
        """连接所有必要的信号和槽"""
        self.ui.action1_3.triggered.connect(self.select_directory)
        self.ui.action.triggered.connect(self.select_directory)
        self.ui.action2_3.triggered.connect(self.clear_tree)
        self.ui.action_2.triggered.connect(self.clear_tree)
        self.ui.action3_2.triggered.connect(self.toggle_tree_view)
        self.ui.action_8.triggered.connect(self.zoom_in)
        self.ui.action_9.triggered.connect(self.zoom_out)
        self.ui.action_4.triggered.connect(self.invert_colors)
        self.ui.action_5.triggered.connect(self.grayscale_image)
        self.ui.action_10.triggered.connect(self.original_size)
        self.ui.action_3.triggered.connect(self.rotate_image)
        self.ui.action1_4.triggered.connect(self.zoom_in)
        self.ui.action2_4.triggered.connect(self.zoom_out)
        self.ui.action3_3.triggered.connect(self.original_size)
        self.ui.action_6.triggered.connect(self.save_image)
        self.ui.action_11.triggered.connect(self.confirm_and_exit)
        self.ui.action1_5.triggered.connect(self.open_link)
        self.ui.action2_5.triggered.connect(lambda: QMessageBox.aboutQt(self, "关于QT"))
        self.ui.treeWidget_3.itemClicked.connect(self.on_tree_item_clicked)
        self.updateStatusBar.connect(self.on_update_status_bar)

    def disable_toolbar_buttons(self):
        """禁用工具栏按钮"""
        self.ui.action_8.setEnabled(False)
        self.ui.action_9.setEnabled(False)
        self.ui.action_10.setEnabled(False)
        self.ui.action_3.setEnabled(False)
        self.ui.action_4.setEnabled(False)
        self.ui.action_5.setEnabled(False)

    def enable_toolbar_buttons(self):
        """启用工具栏按钮"""
        self.ui.action_8.setEnabled(True)
        self.ui.action_9.setEnabled(True)
        self.ui.action_10.setEnabled(True)
        self.ui.action_3.setEnabled(True)
        self.ui.action_4.setEnabled(True)
        self.ui.action_5.setEnabled(True)

    def select_directory(self):
        """选择目录并填充目录树"""
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "选择目录")
        if directory:
            self.ui.treeWidget_3.clear()
            self.populate_tree(directory)
            self.updateStatusBar.emit(f"当前目录: {directory}")
            self.ui.treeWidget_3.show()
            self.ui.action3_2.setText("隐藏目录树")
            self.ui.action3_2.setEnabled(True)
            self.tree_visible = True
            self.disable_toolbar_buttons()

    def populate_tree(self, directory, parent_item=None):
        """递归填充目录树"""
        folder_icon = QtGui.QIcon(get_resource_path("res/文件夹.png"))
        image_icon = QtGui.QIcon(get_resource_path("res/图片.png"))

        if parent_item is None:
            root_item = QtWidgets.QTreeWidgetItem(self.ui.treeWidget_3, [os.path.basename(directory)])
            root_item.setIcon(0, folder_icon)
            self.ui.treeWidget_3.addTopLevelItem(root_item)
        else:
            root_item = parent_item

        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)
            if os.path.isdir(full_path):
                dir_item = QtWidgets.QTreeWidgetItem(root_item, [entry])
                dir_item.setIcon(0, folder_icon)
                root_item.addChild(dir_item)
                self.populate_tree(full_path, dir_item)
            elif entry.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                file_item = QtWidgets.QTreeWidgetItem(root_item, [entry])
                file_item.setIcon(0, image_icon)
                file_item.setData(0, QtCore.Qt.UserRole, full_path)
                root_item.addChild(file_item)

    def zoom_in(self):
        """放大图像"""
        current_pixmap = self.image_label.pixmap()
        if current_pixmap:
            image_array = pixmap_to_array(current_pixmap)
            new_size = (int(image_array.shape[1] * 1.2), int(image_array.shape[0] * 1.2))
            resized_image = cv2.resize(image_array, new_size, interpolation=cv2.INTER_CUBIC)
            new_pixmap = array_to_pixmap(resized_image)
            self.image_label.setPixmap(new_pixmap)
            self.ui.action_6.setEnabled(True)
            self.image_modified = True

    def zoom_out(self):
        """缩小图像"""
        current_pixmap = self.image_label.pixmap()
        if current_pixmap:
            image_array = pixmap_to_array(current_pixmap)
            new_size = (int(image_array.shape[1] * 0.8), int(image_array.shape[0] * 0.8))
            resized_image = cv2.resize(image_array, new_size, interpolation=cv2.INTER_CUBIC)
            new_pixmap = array_to_pixmap(resized_image)
            self.image_label.setPixmap(new_pixmap)
            self.ui.action_6.setEnabled(True)
            self.image_modified = True

    def invert_colors(self):
        """反转图像颜色"""
        current_pixmap = self.image_label.pixmap()
        if current_pixmap:
            new_pixmap = image_operations.invert_colors(current_pixmap)
            self.image_label.setPixmap(new_pixmap)
            self.ui.action_6.setEnabled(True)
            self.image_modified = True

    def grayscale_image(self):
        """将图像转换为灰度"""
        current_pixmap = self.image_label.pixmap()
        if current_pixmap:
            image = current_pixmap.toImage()
            width, height, channels = image.width(), image.height(), 4
            ptr = image.bits()
            ptr.setsize(image.byteCount())
            arr = np.array(ptr).reshape(height, width, channels)

            rgb_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
            gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)

            gray_qimage = QtGui.QImage(gray_image.data, gray_image.shape[1], gray_image.shape[0], gray_image.strides[0],
                                       QtGui.QImage.Format_Grayscale8)
            gray_pixmap = QtGui.QPixmap.fromImage(gray_qimage)
            self.image_label.setPixmap(gray_pixmap)
            self.ui.action_6.setEnabled(True)
            self.image_modified = True

    def original_size(self):
        """恢复图像到原始大小"""
        if self.original_pixmap:
            self.image_label.setPixmap(self.original_pixmap)
            self.ui.action_6.setEnabled(True)
            self.image_modified = True

    def rotate_image(self):
        """旋转图像"""
        current_pixmap = self.image_label.pixmap()
        if current_pixmap:
            new_pixmap = image_operations.rotate(current_pixmap, self.rotation_angle)
            self.image_label.setPixmap(new_pixmap)
            self.ui.action_6.setEnabled(True)
            self.image_modified = True

    def clear_tree(self):
        """清空目录树和图像"""
        self.ui.treeWidget_3.clear()
        self.image_label.clear()
        self.updateStatusBar.emit("目录树已清空")
        self.ui.action3_2.setEnabled(False)
        self.disable_toolbar_buttons()
        self.ui.action_6.setEnabled(False)
        self.image_modified = False

    def toggle_tree_view(self):
        """切换目录树的可见性"""
        if self.tree_visible:
            self.ui.treeWidget_3.hide()
            self.ui.action3_2.setText("显示目录树")
            self.updateStatusBar.emit("目录树已隐藏")
        else:
            self.ui.treeWidget_3.show()
            self.ui.action3_2.setText("隐藏目录树")
            self.updateStatusBar.emit("目录树已显示")
        self.tree_visible = not self.tree_visible

    def on_tree_item_clicked(self, item, column):
        """当目录树中的项被点击时"""
        file_path = item.data(0, QtCore.Qt.UserRole)

        if file_path and os.path.isfile(file_path) and file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            pixmap = QtGui.QPixmap(file_path)
            self.image_label.setPixmap(pixmap)
            self.original_pixmap = pixmap
            self.updateStatusBar.emit(f"显示图片: {file_path}")
            self.enable_toolbar_buttons()
            self.ui.menu_2.setEnabled(True)
            self.ui.action1_4.setEnabled(True)
            self.ui.action2_4.setEnabled(True)
            self.ui.action3_3.setEnabled(True)
            self.image_modified = False
            self.ui.action_6.setEnabled(True)
        else:
            self.disable_toolbar_buttons()
            self.ui.menu_2.setEnabled(False)
            self.ui.action1_4.setEnabled(False)
            self.ui.action2_4.setEnabled(False)
            self.ui.action3_3.setEnabled(False)
            self.ui.action_6.setEnabled(False)

    def save_image(self):
        """保存当前图像"""
        current_pixmap = self.image_label.pixmap()
        if current_pixmap:
            file_dialog = QtWidgets.QFileDialog(self)
            save_path, _ = file_dialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.xpm *.jpg)")
            if save_path:
                current_pixmap.save(save_path)
                self.image_modified = False
                QMessageBox.information(self, "Save Image", "保存成功!")

    def closeEvent(self, event):
        """处理关闭事件"""
        self.confirm_and_exit()
        event.ignore()

    @QtCore.pyqtSlot(str)
    def on_update_status_bar(self, message):
        """更新状态栏消息"""
        self.statusBar().showMessage(message)

    def confirm_and_exit(self):
        """确认并退出应用程序"""
        if self.image_modified:
            reply = QMessageBox.question(
                self, 'Message',
                "您有未保存的更改。您想在退出前保存吗？",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Cancel
            )

            if reply == QMessageBox.Yes:
                self.save_image()
                QtWidgets.qApp.quit()
            elif reply == QMessageBox.No:
                QtWidgets.qApp.quit()
        else:
            QtWidgets.qApp.quit()

    def open_link(self):
        """打开指定的链接"""
        url = QUrl("https://github.com/koliner")
        QDesktopServices.openUrl(url)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())