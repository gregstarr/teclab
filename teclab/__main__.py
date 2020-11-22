import logging
import os
import datetime

from teclab.app import App


date_string = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_fn = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', f'{date_string}_info.log'))
logging.basicConfig(filename=log_fn,
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filemode='w')

app = App()
app.start()
