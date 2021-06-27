from database import Database

from utils import load_config
from torrent import Torrent
from torrent_collection import Torrent_collection
from tracker import Tracker, Tracker_collection
from output import Output

CONFIG = "config/mgmt.toml"
config = load_config(CONFIG)

db = Database(config)
# db.integrety_chk()
# db.info()

torrent_collection = Torrent_collection(db, config)
output = Output(torrent_collection)

# torrent_collection.info()
torrent_collection._load_all_from_db()
# torrent_collection.info()

output.generate()
# exit()

torrent_collection.populate(count=10, collection="books")
torrent_collection.populate(count=10, collection="scimag")
torrent_collection.populate(count=10, collection="fiction")

# torrent_collection.info()
# torrent_collection.peer_crawl(1)

for loop in range(100):
    for collection in ["books", "scimag", "fiction"]:
        torrent_collection.peer_crawl(1)
