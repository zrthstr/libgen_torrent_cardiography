
# find first missing torrent
# fetch & save file in dir
# read data & store:
#   tracker info
#   torrent info
#
#   todo:
#   * add uniqe and primary key for torrents and tracker

import toml
import dataset
import requests
import libtorrent as lt
from pathlib import Path
from datetime import datetime

from db import Db
from tor import Tor
from tracker import Tracker

CONFIG = "config/mgmt.toml"

#TORRENT_DIR = Path("data/torrent")
#TORRENT_SRC = "https://libgen.is/repository_torrent/"

db = dataset.connect('sqlite:///data/ltc.sqlite')

HTTP_GET_RETRY = 1

global tracker


tracker = db['tracker']
torrent = db['torrent']
log = db['log']


def load_config():
    return toml.load(CONFIG)

sqll = Db(db)
#sqll.integrety_chk()
#sqll.info()

config = load_config()
#print(config)

#Tor.integrety_check_libgen()
#Tor.populate(db, config, count=160, only_count_absent=True)

Tor.peer_crawl(db, config, count=2)


#ttt = Tor(10, db, config)
#print(ttt)
#ttt.info()


