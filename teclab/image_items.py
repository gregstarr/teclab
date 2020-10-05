import pyqtgraph as pg
import numpy as np
from PyQt5.Qt import Qt
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic_2d

from teclab import utils


class PolarImageItem(pg.ImageItem):
    pass


class TecMapImageItem(pg.ImageItem):

    def __init__(self, theta, r, **kwargs):
        self.theta = theta
        self.r = r

        self.fig = plt.figure(figsize=(10, 10), dpi=100, tight_layout=True)
        plt.close(self.fig)
        self.ax = self.fig.add_subplot(projection='polar')
        rgba = self.update_and_get_pixels()
        super().__init__(rgba, opacity=1, border=pg.mkPen('r', width=3), **kwargs)

    def set_tec_map(self, tec_map_data, **pcm_kwargs):
        rgba = self.update_and_get_pixels(tec_map_data, **pcm_kwargs)
        self.setImage(rgba)

    def update_and_get_pixels(self, polar_img=None, **pcm_kwargs):
        self.ax.clear()
        if polar_img is not None:
            self.ax.pcolormesh(self.theta, self.r, polar_img, shading='nearest', **pcm_kwargs)
        self.format_polar_mag_ax()
        self.fig.patch.set_alpha(0)
        self.ax.patch.set_alpha(0)
        self.fig.canvas.draw()
        rgba = np.array(self.fig.canvas.buffer_rgba())
        plt.close(self.fig)
        return np.swapaxes(rgba[::-1], 0, 1)

    def format_polar_mag_ax(self):
        self.ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False,
                       labeltop=False, labelleft=False, labelright=False)
        self.ax.set_ylim(0, 60)
        self.ax.set_xticks(np.arange(8) * np.pi / 4)
        self.ax.set_xticklabels((np.arange(8) * 3 + 6) % 24)
        self.ax.set_yticks([10, 20, 30, 40, 50])
        self.ax.set_yticklabels([80, 70, 60, 50, 40])
        self.ax.grid()
        self.ax.tick_params(axis='x', which='both', bottom=True, labelbottom=True)
        self.ax.tick_params(axis='y', which='both', left=True, labelleft=True, width=0, length=0)
        self.ax.set_rlabel_position(80)


class HoverImage(pg.ImageItem):

    def __init__(self, image=None, **kargs):
        super().__init__(image, opacity=1, compositionMode=pg.QtGui.QPainter.CompositionMode_Plus, **kargs)
        self.set_kernel(15)

    def set_kernel(self, size):
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

    def __init__(self, c, bg_img_item, **kargs):
        self.bg_img_item = bg_img_item
        super().__init__(np.zeros(self.bg_img_item.image.shape[:2] + (3,)),
                         compositionMode=pg.QtGui.QPainter.CompositionMode_Plus, opacity=1, **kargs)
        self.color_channel = DrawingImage.colors[c]
        self.set_kernel(15)
        self.x = None
        self.y = None

    def reset_img(self):
        self.setImage(np.zeros_like(self.image))

    def get_labels(self):
        label_img = np.swapaxes(self.image, 0, 1)[:, :, self.color_channel]
        y = np.arange(label_img.shape[0])
        x = np.arange(label_img.shape[1])
        X, Y = np.meshgrid(x, y)
        xy = np.column_stack((X.ravel(), Y.ravel()))
        tr = self.bg_img_item.ax.transData.inverted().transform(xy)

        theta_grid = self.bg_img_item.theta
        r_grid = self.bg_img_item.r
        dt = np.diff(theta_grid[0]).mean()
        dr = abs(np.diff(r_grid[:, 0]).mean())
        theta_bins = np.concatenate((theta_grid[0] - dt / 2, [theta_grid[0, -1] + dt / 2]))
        r_bins = np.concatenate(([r_grid[0, 0] + dr / 2], r_grid[:, 0] - dr / 2))[::-1]
        tr[tr[:, 0] > theta_bins.max(), 0] -= 2 * np.pi
        tr[tr[:, 0] < theta_bins.min(), 0] += 2 * np.pi

        res = binned_statistic_2d(tr[:, 0], tr[:, 1], label_img.ravel(), bins=[theta_bins, r_bins])
        labels = res.statistic.T[::-1] > .5
        return labels

    def set_kernel(self, size):
        self.centerValue = int((size - 1) / 2)
        self.kern = np.zeros((size, size, 3), dtype=np.uint8)
        self.mask = np.zeros((size, size, 3), dtype=np.uint8)
        y, x = np.mgrid[-self.centerValue:size - self.centerValue, -self.centerValue:size - self.centerValue]
        self.mask[:, :, :] = (x * x + y * y <= (size - 1) / 2 * (size - 1) / 2)[:, :, None]
        self.kern[:, :, self.color_channel] = 255

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
