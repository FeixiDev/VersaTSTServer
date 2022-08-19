# -*- coding: utf-8 -*-

from performance_app import create_app
from kraken.sshv import utils as utils
from kraken.sshv import log as log
import sys 
sys.path.append("..")
#import log

#log.Log.filename = log.WEB_LOG_NAME
#logger = log.Log()
utils._init()
logger = log.Log()
utils.set_logger(logger)
app = create_app()

if __name__ == '__main__':
  app.run(host='0.0.0.0',  # 任何ip都可以访问
      port=7777,  # 端口
      debug=True,
      threaded=True
      )

