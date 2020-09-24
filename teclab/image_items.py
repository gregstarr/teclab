import pyqtgraph as pg
import numpy as np
from PyQt5.Qt import Qt

from teclab import utils


class TecMapImageItem(pg.ImageItem):

    def __init__(self, theta, r, **kwargs):
        super().__init__(np.zeros((500, 500)), **kwargs)
        self.theta = theta
        self.delta_theta = (self.theta[1, 1] - self.theta[0, 0]) * 180 / np.pi
        self.r = r
        self.delta_r = self.r[1, 1] - self.r[0, 0]
        x = self.r * np.cos(self.theta)
        self.x_bounds = (x.min(), x.max())
        y = self.r * np.sin(self.theta)
        self.y_bounds = (y.min(), y.max())

    def set_tec_map(self, tec_map_data):
        x = np.linspace(*self.x_bounds, 500)
        y = np.linspace(*self.y_bounds, 500)
        img_data = utils.polar_to_cart(tec_map_data.T, self.delta_theta, self.delta_r, x, y)
        self.setImage(img_data)


class HoverImage(pg.ImageItem):

    def __init__(self, image=None, **kargs):
        pg.ImageItem.__init__(self, image, opacity=1, compositionMode=pg.QtGui.QPainter.CompositionMode_Plus, **kargs)
        self.setKernel(5)

    def setKernel(self, size):
        self.centerValue = int((size - 1) / 2)
        self.kern = np.zeros((size, size), dtype=np.uint8) * 255
        y, x = np.mgrid[-self.centerValue:size - self.centerValue, -self.centerValue:size - self.centerValue]
        mask = x * x + y * y <= (size - 1) / 2 * (size - 1) / 2
        self.kern[mask] = 255
        self.setDrawKernel(self.kern, center=(self.centerValue, self.centerValue))

    def hoverEvent(self, event):
        if not event.isExit():
            self.image[:, :] = 0
            self.updateImage()
            self.drawAt(event.pos(), event)
        else:
            self.image[:, :] = 0
            self.updateImage()


class DrawingImage(pg.ImageItem):
    colors = {'r': 0, 'g': 1, 'b': 2}

    def __init__(self, c, image=None, **kargs):
        pg.ImageItem.__init__(self, image, compositionMode=pg.QtGui.QPainter.CompositionMode_Plus, opacity=1, **kargs)
        self.c = c
        self.setKernel(5)
        self.x = None
        self.y = None

    def setKernel(self, size):
        self.centerValue = int((size - 1) / 2)
        self.kern = np.zeros((size, size, 3), dtype=np.uint8)
        self.mask = np.zeros((size, size, 3), dtype=np.uint8)
        y, x = np.mgrid[-self.centerValue:size - self.centerValue, -self.centerValue:size - self.centerValue]
        self.mask[:, :, :] = (x * x + y * y <= (size - 1) / 2 * (size - 1) / 2)[:, :, None]
        self.kern[:, :, DrawingImage.colors[self.c]] = 255

    def mouseClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setDrawKernel(self.kern, self.mask, center=(self.centerValue, self.centerValue))
            self.drawAt(event.pos(), event)
        if event.button() == Qt.RightButton:
            self.setDrawKernel(self.kern * 0, self.mask, center=(self.centerValue, self.centerValue))
            self.drawAt(event.pos(), event)

    def mouseDragEvent(self, event):
        if event.isStart():
            if event.button() == Qt.LeftButton:
                self.setDrawKernel(self.kern, self.mask, center=(self.centerValue, self.centerValue))
            if event.button() == Qt.RightButton:
                self.setDrawKernel(self.kern * 0, self.mask, center=(self.centerValue, self.centerValue))
        if event.button() in [Qt.LeftButton, Qt.RightButton]:

            pos = event.pos()
            x, y = int(np.round(pos.x())), int(np.round(pos.y()))
            self.drawAt(event.pos(), event)
            if self.x is None or self.y is None:
                self.x = x
                self.y = y
                return
            sx, sy = np.sign(x - self.x), np.sign(y - self.y)

            if sx == 0:
                self.x = x
                self.y = y
                if event.isFinish():
                    self.x = None
                    self.y = None
                return

            if sy == 0:
                self.x = x
                self.y = y
                if event.isFinish():
                    self.x = None
                    self.y = None
                return

            X, Y = np.meshgrid(np.arange(1, abs(x - self.x)) * sx, np.arange(1, abs(y - self.y)) * sy)
            slope = (y - self.y) / (x - self.x)
            if sx == 1 and sy == 1:
                gte = slope >= (2 * Y - 1) / (2 * X + 1)
                lte = slope <= (2 * Y + 1) / (2 * X - 1)
            elif sx == 1 and sy == -1:
                lte = slope <= (2 * Y + 1) / (2 * X + 1)
                gte = slope >= (2 * Y - 1) / (2 * X - 1)
            elif sx == -1 and sy == -1:
                lte = slope <= (2 * Y - 1) / (2 * X + 1)
                gte = slope >= (2 * Y + 1) / (2 * X - 1)
            elif sx == -1 and sy == 1:
                lte = slope <= (2 * Y - 1) / (2 * X - 1)
                gte = slope >= (2 * Y + 1) / (2 * X + 1)

            result = lte * gte
            pixels = np.where(result.T)

            xs = sx * pixels[0] + self.x
            ys = sy * pixels[1] + self.y
            for x1, y1 in zip(xs, ys):
                p = pg.QtCore.QPoint(x1, y1)
                self.drawAt(p)

            self.x = x
            self.y = y

            if event.isFinish():
                self.x = None
                self.y = None

    def hoverEvent(self, event):
        if not event.isExit():
            # the mouse is hovering over the image; make sure no other items
            # will receive left click/drag events from here.
            event.acceptDrags(Qt.LeftButton)
            event.acceptClicks(Qt.LeftButton)
            event.acceptDrags(Qt.RightButton)
            event.acceptClicks(Qt.RightButton)
