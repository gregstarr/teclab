from PyQt5.QtWidgets import *
import pyqtgraph as pg
from pyqtgraph import parametertree
import numpy as np
import h5py

from teclab import image_items

# Base PyQtGraph configuration
pg.setConfigOption('background', (0, 50, 100))
pg.setConfigOption('foreground', 'k')

param_descriptor = [
    {
        'name': 'Basic Params',
        'type': 'group',
        'children': [
            {'name': 'Integer1', 'type': 'int', 'value': 10},
            {'name': 'Integer2', 'type': 'int', 'value': 10},
            {'name': 'Integer3', 'type': 'int', 'value': 10},
        ]
    }
]


class App(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        splitter = QSplitter()

        # DRAWING
        drawing_area_widget = QWidget(splitter)
        drawing_area_layout = QVBoxLayout(drawing_area_widget)
        view = pg.GraphicsView(drawing_area_widget)
        drawing_area_layout.addWidget(view)
        viewbox = pg.ViewBox(lockAspect=True, invertY=False, enableMenu=False)
        view.setCentralItem(viewbox)

        theta, r = np.meshgrid(np.linspace(0, 2 * np.pi, 100), np.linspace(0, 10, 100))
        data = np.sin(theta) * r ** 2

        img_item = image_items.TecMapImageItem(theta, r, opacity=1, border=pg.mkPen('r', width=5))
        viewbox.addItem(img_item)
        img_item.set_tec_map(data)

        draw_img = image_items.DrawingImage('r', np.zeros((500, 500, 3)))
        viewbox.addItem(draw_img)

        hover_img = image_items.HoverImage(np.zeros((500, 500)))
        viewbox.addItem(hover_img)

        # PARAMETERS
        settings_area_widget = QWidget(splitter)
        settings_area_layout = QVBoxLayout(settings_area_widget)
        param_object = parametertree.Parameter.create(name='params', type='group', children=param_descriptor)
        param_tree = parametertree.ParameterTree(parent=settings_area_widget, showHeader=False)
        param_tree.addParameters(param_object)
        settings_area_layout.addWidget(param_tree)

        # TOP LEVEL
        splitter.addWidget(drawing_area_widget)
        splitter.addWidget(settings_area_widget)
        splitter.setStretchFactor(0, 1)
        self.setCentralWidget(splitter)

        self.setWindowTitle("TEC Label Creator")
        self.setGeometry(100, 100, 1200, 600)
        self.show()

    def load_map(self, fn, map_index):
        with h5py.File(fn) as f:
            img_data = f['tec'][()][:, :, map_index]
