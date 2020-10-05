from PyQt5.QtWidgets import QApplication
import numpy as np
import logging

from teclab.gui import Gui
from teclab import config
from teclab import utils

logger = logging.getLogger(__name__)


class App:

    def __init__(self):
        logger.info("Initializing App class")
        self.gui = None
        self.current_map = {
            'year': None,
            'month': None,
            'index': None,
            'datetime': None,
            'unsure': False,
            'h5_file': None,
        }
        self.tec_map = None

    @property
    def map_indicator(self):
        return f"{self.current_map['datetime']} ({self.current_map['year']}, {self.current_map['month']}, {self.current_map['index']})"

    def start(self):
        logger.info("Starting App")
        app = QApplication([])
        self.gui = Gui(self)
        app.exec_()

    def map_save(self):
        if self.tec_map is None:
            logger.info("No map to save")
            return
        logger.info(f"Saving map: {self.current_map}")
        labels = self.gui.get_labels()
        utils.update_h5(self.current_map, labels)
        utils.update_done_list(config.done_list_file, config.done_list, self.current_map)
        utils.update_unsure_list(config.unsure_list_file, config.unsure_list, self.current_map)
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(projection='polar')
        ax.pcolormesh(config.theta_grid, config.radius_grid, labels, shading='flat')
        plt.show()

    def map_next(self):
        year, month, index, datetime = self.get_next_map()
        self.current_map.update(year=year, month=month, index=index, datetime=datetime,
                                h5_file=config.data_file_name.format(year=year, month=month))
        logger.info(f"Getting next map: {self.current_map}")
        self.tec_map, *_ = utils.open_map(self.current_map)
        self.gui.update_map_indicator()
        self.gui.update_tec_map(reset=True)

    @staticmethod
    def get_next_map():
        year = np.random.choice(list(config.map_tree.keys()))
        month = np.random.choice(list(config.map_tree[year].keys()))
        index = np.random.choice(list(config.map_tree[year][month]['index']))
        while (year, month, index) in config.done_list + config.unsure_list:
            year = np.random.choice(list(config.map_tree.keys()))
            month = np.random.choice(list(config.map_tree[year].keys()))
            index = np.random.choice(list(config.map_tree[year][month]['index']))
        datetime = config.map_tree[year][month]['datetime'][index]
        return year, month, index, datetime
