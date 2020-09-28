from PyQt5.QtWidgets import *
from PyQt5 import QtCore
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
        'name': 'Basic Params',
        'type': 'group',
        'children': [
            {'name': 'Brush Size', 'type': 'int', 'value': 5},
            {'name': 'Unsure', 'type': 'bool', 'value': False},
            {'name': 'vmin', 'type': 'int', 'value': 0},
            {'name': 'vmax', 'type': 'int', 'value': 20},
        ]
    }
]


class Gui(QMainWindow):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        splitter = QSplitter()

        # DRAWING
        drawing_area_widget = QWidget(splitter)  # container widget
        drawing_area_layout = QVBoxLayout(drawing_area_widget)  # vertical layout
        # graphics area
        view = pg.GraphicsView(drawing_area_widget)
        drawing_area_layout.addWidget(view)
        viewbox = pg.ViewBox(lockAspect=True, invertY=False, enableMenu=False)
        view.setCentralItem(viewbox)
        self.tec_map_img = image_items.TecMapImageItem(config.theta_grid, config.radius_grid)
        viewbox.addItem(self.tec_map_img)
        self.draw_img = image_items.DrawingImage('r', self.tec_map_img)
        viewbox.addItem(self.draw_img)
        hover_img = image_items.HoverImage(np.zeros((1000, 1000)))
        viewbox.addItem(hover_img)
        # Buttons
        button_area_widget = QWidget(drawing_area_widget)
        drawing_area_layout.addWidget(button_area_widget)
        button_area_layout = QHBoxLayout(button_area_widget)
        save_button = QPushButton("Save")  # UNSURE
        button_area_layout.addWidget(save_button)
        save_button.pressed.connect(self.app.map_save)
        save_button.setFocusPolicy(QtCore.Qt.NoFocus)
        next_button = QPushButton("Next")  # NEXT
        button_area_layout.addWidget(next_button)
        next_button.pressed.connect(self.app.map_next)
        next_button.setFocusPolicy(QtCore.Qt.NoFocus)

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

    def get_labels(self):
        return self.draw_img.get_labels()

    def update_map_indicator(self):
        self.status_bar.showMessage(self.app.map_indicator)

    def update_tec_map(self, tec_map):
        self.tec_map_img.set_tec_map(tec_map)
        self.draw_img.reset_img()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            print("SPACE")
        event.accept()

    def parameter_changed(self, param, changes):
        print("tree changes:")
        for param, change, data in changes:
            path = self.param_object.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
            print('  parameter: %s' % childName)
            print('  change:    %s' % change)
            print('  data:      %s' % str(data))
            print('  ----------')
