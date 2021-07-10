import time
import sys

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

def run_for(minutes=0,seconds=1):
    end = datetime.now() + timedelta(minutes=minutes, seconds=seconds)
    while end > datetime.now():
        run()


def run():
#for loop in range(100):
    for collection in ["books", "scimag", "fiction"]:
        #torrent_collection.populate(count=90, collection=collection)
        torrent_collection.peer_crawl(1)


if __name__ == "__main__":
    info, skip_run, populate =  False, False, False

    torrent_collection = Torrent_collection(db, config)

    for argv in sys.argv[1:]:
        if argv == "output":
            skip_run = True
        if argv == "info":
            info = True
        if argv in ["help", "-h", "--help"]:
            print("tbd..")
            sys.exit()


    # torrent_collection.peer_crawl(1)
    # torrent_collection.info()
    # torrent_collection._load_all_from_db()

    if populate:
        torrent_collection.populate(count=10, collection="books")
        torrent_collection.populate(count=100, collection="scimag")
        torrent_collection.populate(count=10, collection="fiction")

    if info:
        torrent_collection.info()
        torrent_collection.stats()
        sys.exit()


    # torrent_collection.peer_crawl(1)

    if not skip_run:
        run_for(minutes=20, seconds=0)

    #from torrent import Torrent
    #t = Torrent(10, "books", db, config)
    #t.info()

    output = Output(torrent_collection)
    output.generate()
