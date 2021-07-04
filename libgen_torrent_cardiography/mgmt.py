from database import Database
from datetime import datetime, timedelta

from utils import load_config
from torrent_collection import Torrent_collection
from output import Output

CONFIG = "config/mgmt.toml"
config = load_config(CONFIG)
db = Database(config)
# db.integrety_chk()
# db.info()

def run_for(minutes):
    end = datetime.now() + timedelta(minutes=minutes)
    while end < datetime.now():
        run()


def run()
    for loop in range(100):
        for collection in ["books", "scimag", "fiction"]:
            torrent_collection.populate(count=30, collection=collection)
            torrent_collection.peer_crawl(1)


torrent_collection = Torrent_collection(db, config)
output = Output(torrent_collection)

#torrent_collection.peer_crawl(1)

#output.generate()

# torrent_collection.info()
# torrent_collection._load_all_from_db()

# exit()

#torrent_collection.populate(count=10, collection="books")
#torrent_collection.populate(count=10, collection="scimag")
#torrent_collection.populate(count=10, collection="fiction")

# torrent_collection.info()
# torrent_collection.peer_crawl(1)

run_for(4)

output.generate()
