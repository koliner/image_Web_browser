# image_operations.py

from PyQt5 import QtGui, QtCore
from PIL import Image
import numpy as np

def pixmap_to_numpy(pixmap):
    """Convert QPixmap to a numpy array."""
    image = pixmap.toImage()
    image = image.convertToFormat(QtGui.QImage.Format_RGBA8888)
    width = image.width()
    height = image.height()
    ptr = image.bits()
    ptr.setsize(image.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)
    return arr

def numpy_to_pixmap(arr):
    """Convert numpy array back to QPixmap."""
    height, width, channel = arr.shape
    bytesPerLine = 4 * width
    image = QtGui.QImage(arr.data, width, height, bytesPerLine, QtGui.QImage.Format_RGBA8888)
    return QtGui.QPixmap.fromImage(image)


def invert_colors(pixmap):
    arr = pixmap_to_numpy(pixmap)
    arr[..., :3] = 255 - arr[..., :3]  # Invert colors
    return numpy_to_pixmap(arr)


def grayscale_image(self):
    current_pixmap = self.image_label.pixmap()
    if current_pixmap:
        # 将 QPixmap 转换为 QImage
        image = current_pixmap.toImage()

        # 将图像转换为灰度
        gray_image = image.convertToFormat(QtGui.QImage.Format_Grayscale8)

        # 将灰度图像转换回 QPixmap
        gray_pixmap = QtGui.QPixmap.fromImage(gray_image)

        # 更新 QLabel 显示
        self.image_label.setPixmap(gray_pixmap)


def rotate(pixmap, angle):
    """Rotate the image by the given angle."""
    arr = pixmap_to_numpy(pixmap)
    image = Image.fromarray(arr)
    image = image.rotate(angle, expand=True)
    arr = np.array(image)
    return numpy_to_pixmap(arr)


def original_size(self):
    """Restore the image to its original size."""
    if self.original_pixmap:
        new_pixmap = self.original_pixmap.scaled(self.original_size, QtCore.Qt.KeepAspectRatio)
        self.image_label.setPixmap(new_pixmap)