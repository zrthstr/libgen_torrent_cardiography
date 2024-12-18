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

def usage():
    print("TBD")
    sys.exit()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        usage()


    options = dict(
            info = False,
            scrape = False,
            populate = False,
            output = False,
            help = False,
            )

    for k,v in options.items():
        if k in sys.argv:
            options[k] = True


    torrent_collection = Torrent_collection(db, config)
    # torrent_collection.peer_crawl(1)
    # torrent_collection.info()
    # torrent_collection._load_all_from_db()
    # torrent_collection.peer_crawl(1)


    #from torrent import Torrent
    #t = Torrent(10, "books", db, config)
    #t.info()


    if options["help"]:
        usage()

    if options["info"]:
        torrent_collection.info()
        torrent_collection.stats()
        sys.exit()

    if options["populate"]:
        torrent_collection.populate(count=20, collection="books")
        torrent_collection.populate(count=20, collection="scimag")
        torrent_collection.populate(count=20, collection="fiction")

    if options["scrape"]:
        run_for(minutes=20, seconds=0)

    if options["output"]:
        output = Output(torrent_collection)
        output.generate()



