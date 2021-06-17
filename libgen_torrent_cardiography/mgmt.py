#   todo:
#   * add uniqe/primary key for torrents and tracker

from database import Database

from utils import load_config
#from tor import Tor
from torrent import Torrent
from torrent_collection import Torrent_collection
from tracker import Tracker, Tracker_collection

CONFIG = "config/mgmt.toml"

# move tp config
HTTP_GET_RETRY = 1  ## move to config

config = load_config(CONFIG)

db = Database()
#db.integrety_chk()
#db.info()


torrent_collection = Torrent_collection(db, config)

torrent_collection.info()
torrent_collection._load_all_from_db()
torrent_collection.info()

#print("newest")
#torrent_collection.newest()
torrent_collection.populate(count=1)
#torrent_collection.info()

torrent_collection.peer_crawl()
#ttt = Tor(10, db, config)
#print(ttt)
#ttt.info()


