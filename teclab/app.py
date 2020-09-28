from PyQt5.QtWidgets import QApplication
import numpy as np

from teclab.gui import Gui
from teclab import config
from teclab import utils


class App:

    def __init__(self):
        self.gui = None
        self.current_map = {
            'year': None,
            'month': None,
            'index': None,
            'datetime': None,
            'unsure': False,
            'h5_file': None,
        }

    @property
    def map_indicator(self):
        return str(self.current_map['datetime'])

    def start(self):
        app = QApplication([])
        self.gui = Gui(self)
        app.exec_()

    def map_save(self):
        labels = self.gui.get_labels()
        utils.update_h5(self.current_map, labels)
        utils.update_done_list(config.done_list_file, config.done_list, self.current_map)
        utils.update_unsure_list(config.unsure_list_file, config.unsure_list, self.current_map)

    def map_next(self):
        year, month, index, datetime = self.get_next_map()
        self.current_map.update(year=year, month=month, index=index, datetime=datetime,
                                h5_file=config.data_file_name.format(year=year, month=month))
        tec_map, *_ = utils.open_map(self.current_map)
        self.gui.update_map_indicator()
        self.gui.update_tec_map(tec_map)

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
