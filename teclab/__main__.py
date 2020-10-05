import logging
import os
import datetime

import teclab


date_string = datetime.datetime.now().strftime("%Y%M%d_%H%m%S")
log_fn = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', f'{date_string}_info.log'))
logging.basicConfig(filename=log_fn,
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filemode='w')

app = teclab.App()
app.start()
