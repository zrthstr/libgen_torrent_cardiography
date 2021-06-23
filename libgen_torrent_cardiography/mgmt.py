#   todo:
#   * add uniqe/primary key for torrents and tracker

from database import Database

import random

from utils import load_config
from torrent import Torrent
from torrent_collection import Torrent_collection
from tracker import Tracker, Tracker_collection
from output import Output

CONFIG = "config/mgmt.toml"

# move tp config
HTTP_GET_RETRY = 1  ## move to config

config = load_config(CONFIG)

db = Database()
#db.integrety_chk()
#db.info()

output = Output(db, config)


torrent_collection = Torrent_collection(db, config)

#torrent_collection.info()
torrent_collection._load_all_from_db()
#torrent_collection.info()

#print("newest")
#torrent_collection.newest()

torrent_collection.populate(count=10, collection="books")
torrent_collection.populate(count=10, collection="scimag")
torrent_collection.populate(count=10, collection="fiction")

#torrent_collection.info()

#torrent_collection.peer_crawl(1)

for loop in range(100):
    #for collection in ["books", "scimag", "fiction"]:
    for collection in ["fiction"]:
        torrent_collection.populate(count=10, collection=collection)
        torrent_collection.peer_crawl(1)
        print("loop", loop)


        ## this causes a problem if the id is out of scope
        ## we could add check that we have in collection populate to torrent
        #ttt = Torrent(random.randint(0,50), collection, db, config)
        #ttt.info()

    output.generate()
