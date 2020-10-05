from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
import pyqtgraph as pg
from pyqtgraph import parametertree
import numpy as np
import matplotlib.pyplot as plt

from teclab import image_items
from teclab import config

# Base PyQtGraph configuration
pg.setConfigOption('background', (100, 100, 100))
pg.setConfigOption('foreground', 'k')

param_descriptor = [
    {
        'name': 'Image',
        'type': 'group',
        'children': [
            {'name': 'vmin', 'type': 'float', 'value': 0},
            {'name': 'vmax', 'type': 'float', 'value': 20},
        ]
    },
    {
        'name': 'Editing',
        'type': 'group',
        'children': [
            {'name': 'Brush Size', 'type': 'int', 'value': 15},
        ]
    },
    {
        'name': 'Misc',
        'type': 'group',
        'children': [
            {'name': 'Unsure', 'type': 'bool', 'value': False},
        ]
    },
]


class Gui(QMainWindow):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.pcm_params = {'vmin': 0, 'vmax': 20}

        splitter = QSplitter()

        # DRAWING
        drawing_area_widget = QWidget(splitter)  # container widget
        drawing_area_layout = QVBoxLayout(drawing_area_widget)  # vertical layout
        # graphics area
        graphics_layout = pg.GraphicsLayoutWidget(drawing_area_widget)
        drawing_area_layout.addWidget(graphics_layout)
        self.viewbox = graphics_layout.addViewBox(lockAspect=True, invertY=False, enableMenu=False)
        self.tec_map_img = image_items.TecMapImageItem(config.theta_grid, config.radius_grid)
        self.viewbox.addItem(self.tec_map_img)
        self.draw_img = image_items.DrawingImage('r', self.tec_map_img)
        self.viewbox.addItem(self.draw_img)
        self.hover_img = image_items.HoverImage(np.zeros((1000, 1000)))
        self.viewbox.addItem(self.hover_img)
        # Buttons
        button_area_widget = QWidget(drawing_area_widget)
        drawing_area_layout.addWidget(button_area_widget)
        button_area_layout = QHBoxLayout(button_area_widget)
        self._add_button("Clean", button_area_layout, self.map_clean)
        self._add_button("Save", button_area_layout, self.app.map_save)
        self._add_button("Next", button_area_layout, self.app.map_next)

        # cross section plot
        self.cross_section_plot = graphics_layout.addPlot()
        self.cross_section_plot.setMaximumWidth(300)
        self.cross_section_plot.setLimits(minXRange=10, maxXRange=40, yMin=30, yMax=90, xMin=0)
        self.cross_section_line = self.cross_section_plot.plot()
        self.cross_section_mlat = pg.InfiniteLine(angle=0)
        self.cross_section_plot.addItem(self.cross_section_mlat)
        self.proxy = pg.SignalProxy(self.hover_img.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        # status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.app.map_indicator)

        # PARAMETERS
        settings_area_widget = QWidget(splitter)
        settings_area_layout = QVBoxLayout(settings_area_widget)
        self.param_object = parametertree.Parameter.create(name='params', type='group', children=param_descriptor)
        self.param_object.sigTreeStateChanged.connect(self.parameter_changed)
        param_tree = parametertree.ParameterTree(parent=settings_area_widget, showHeader=False)
        param_tree.addParameters(self.param_object)
        settings_area_layout.addWidget(param_tree)

        # TOP LEVEL
        splitter.addWidget(drawing_area_widget)
        splitter.addWidget(settings_area_widget)
        splitter.setStretchFactor(0, 1)
        self.setCentralWidget(splitter)

        self.setWindowTitle("TEC Label Creator")
        self.setGeometry(100, 100, 1200, 600)
        self.show()

    def mouseMoved(self, evt):
        pos = evt[0]
        if self.hover_img.sceneBoundingRect().contains(pos) and self.app.tec_map is not None:
            mousePoint = self.viewbox.mapSceneToView(pos)
            t, r = self.tec_map_img.ax.transData.inverted().transform((mousePoint.x(), mousePoint.y()))
            if t < config.theta_vals.min():
                t += 2 * np.pi
            elif t > config.theta_vals.max():
                t -= 2 * np.pi
            t_ind = np.argmin(abs(config.theta_vals - t))
            data = np.nanmean(self.app.tec_map[:, t_ind-3:t_ind+4], axis=1)
            m = 3
            pad_width = (m - 1) // 2
            data = np.pad(data, (pad_width, pad_width), mode='edge')
            data = np.nanmedian(np.column_stack([data[i:data.shape[0] + 1 - m + i] for i in range(m)]), axis=1)
            self.cross_section_line.setData(data, 90 - config.radius_vals)
            self.cross_section_mlat.setPos(90 - r)

    def get_labels(self):
        return self.draw_img.get_labels()

    def update_map_indicator(self):
        self.status_bar.showMessage(self.app.map_indicator)

    def update_tec_map(self, reset=False):
        self.tec_map_img.set_tec_map(self.app.tec_map, **self.pcm_params)
        if reset:
            self.draw_img.reset_img()
            self.param_object.child('Misc', 'Unsure').setValue(False)

    def map_clean(self):
        print("clean")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            print("SPACE")
        event.accept()

    def parameter_changed(self, param, changes):
        for param, change, data in changes:
            path = self.param_object.childPath(param)
            if path[0] == 'Image':
                self.pcm_params[path[1]] = data
                self.update_tec_map()
            if path[0] == 'Editing':
                if path[1] == 'Brush Size':
                    self.draw_img.set_kernel(data)
                    self.hover_img.set_kernel(data)
            if path[0] == 'Misc':
                if path[1] == 'Unsure':
                    self.app.current_map['unsure'] = data

    def _add_button(self, name, layout, callback, no_focus=True):
        button = QPushButton(name)
        layout.addWidget(button)
        button.pressed.connect(callback)
        if no_focus:
            button.setFocusPolicy(QtCore.Qt.NoFocus)
