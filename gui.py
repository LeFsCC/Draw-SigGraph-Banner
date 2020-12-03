import sys

import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QRadioButton
from PyQt5.QtGui import QPainter, QPixmap, QPen
from PyQt5.QtCore import Qt, QPoint
from math import sqrt
import numpy as np

path = "data/grass.png"
res_path = "data/opencv-mixed-clone-example.jpg"
flowers_path = ["data/flower1.jpg", "data/flower2.jpg", "data/flower3.jpg"]
threshold = 40


class Point:
    def __init__(self, x, y, t):
        self.x = x
        self.y = y
        self.t = t


class Winform(QWidget):
    def __init__(self, parent=None):
        super(Winform, self).__init__(parent)
        self.setWindowTitle("SIGGRAPH BANNER")
        self.pix = QPixmap(path)
        self.lastPoint = QPoint()
        self.endPoint = QPoint()
        self.clear_btn = QPushButton(self)
        self.show_btn = QPushButton(self)

        self.flower1_btn = QRadioButton("yellow", self)
        self.flower2_btn = QRadioButton("purple", self)
        self.flower3_btn = QRadioButton("white", self)

        self.lab = QLabel()
        self.init_view()
        self.points = []
        self.clear_mark = False
        self.cur_flower_index = 0

        self.im = []

    def init_view(self):
        self.resize(1200, 700)
        self.pix = QPixmap(path)

        self.clear_btn.setText("clear")
        self.clear_btn.resize(100, 30)
        self.clear_btn.move(1050, 100)
        self.clear_btn.clicked.connect(self.clear_canvas)

        self.show_btn.setText("result")
        self.show_btn.resize(100, 30)
        self.show_btn.move(1050, 150)
        self.show_btn.clicked.connect(self.show_picture)

        self.flower1_btn.move(1050, 240)
        self.flower1_btn.toggled.connect(self.flower1_on_click)

        self.flower2_btn.move(1050, 280)
        self.flower2_btn.toggled.connect(self.flower2_on_click)

        self.flower3_btn.move(1050, 320)
        self.flower3_btn.toggled.connect(self.flower3_on_click)

        self.lab.setPixmap(self.pix)

    def flower1_on_click(self):
        self.cur_flower_index = 0

    def flower2_on_click(self):
        self.cur_flower_index = 1

    def flower3_on_click(self):
        self.cur_flower_index = 2

    def clear_canvas(self):
        self.points.clear()
        self.clear_mark = True
        self.update()

    def show_picture(self):
        cv2.imwrite(res_path, self.im)
        cv2.imshow("result", self.im)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def distance(self, p1, p2):
        return sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def split_points(self):
        if len(self.points) == 0:
            return []
        start_point = self.points[0]
        sp_ps = [start_point]

        for i in range(1, len(self.points) - 1):
            dis = self.distance(start_point, self.points[i])
            if dis > threshold:
                sp_ps.append(self.points[i])
                start_point = self.points[i]
        return sp_ps

    def paintEvent(self, event):
        if self.clear_mark:
            self.clear_mark = False
            main_painter = QPainter(self)
            self.pix = QPixmap(path)
            main_painter.drawPixmap(0, 0, self.pix)
            return

        painter = QPainter(self.pix)
        painter.begin(self.pix)
        pen = QPen(Qt.red, 3, Qt.SolidLine)
        painter.setPen(pen)

        pp = QPainter(self.pix)
        pen = QPen()
        pen.setWidth(4)
        pp.setPen(pen)
        pp.drawLine(self.lastPoint, self.endPoint)
        self.lastPoint = self.endPoint
        pp.end()

        temp_points = self.split_points()
        for item in range(len(temp_points)):
            painter.drawPoint(temp_points[item].x, temp_points[item].y)
        painter.end()

        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pix)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clear_mark = False
            self.lastPoint = event.pos()
            p = Point(self.lastPoint.x(), self.lastPoint.y(), self.cur_flower_index)
            self.points.append(p)
            self.endPoint = self.lastPoint

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton:
            self.endPoint = event.pos()
            p = Point(self.endPoint.x(), self.endPoint.y(), self.cur_flower_index)
            self.points.append(p)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.endPoint = event.pos()
            p = Point(self.endPoint.x(), self.endPoint.y(), self.cur_flower_index)
            self.points.append(p)
            self.update()
            self.graph_blend()

    # 图像融合
    def graph_blend(self):
        self.im = cv2.imread("data/grass.png")

        temp_points = self.split_points()
        for item in temp_points:
            center = (item.x, item.y)
            obj = cv2.imread(flowers_path[item.t])
            mask = 255 * np.ones(obj.shape, obj.dtype)
            try:
                self.im = cv2.seamlessClone(obj, self.im, mask, center, 4)
            except:
                pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Winform()
    form.show()
    sys.exit(app.exec_())
