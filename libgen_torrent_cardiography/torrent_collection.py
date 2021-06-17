import requests
import libtorrent as lt
from pathlib import Path
from datetime import datetime
from lib.ttsfix import scraper

from tracker import Tracker, Tracker_collection
from torrent import Torrent

from lib.ttsfix import scraper


HTTP_GET_RETRY = 1  # move to config

#tracker = db['tracker']
#torrent = db['torrent']
#log = db['log']

class Torrent_collection:

    TORRENT_DIR = Path("data/torrent") # get from config!
    TORRENT_SRC = "https://libgen.is/repository_torrent/"

    def __init__(self, db, config):
        self.config = config
        self.base_path = self.TORRENT_DIR
        self.base_url = self.TORRENT_SRC

        self.db = db

        #self.db.tracker = db.tracker
        #self.db.torrent = db.torrent
        #self.db.log = db.log

        self.members = self._load_all_from_db()

    def info(self):
        for tor in self.members:
            print(tor)


    def _load_all_from_db(self):
        return [ tor for tor in self.db.torrent.find()]


    def newest(self):
        ## TODO, chek if "-" or "" is correct
        #last = torrent.find_one(order_by='-file_name')
        last = self.db.torrent.find_one(order_by='-id')
        if last == None:
            return 0
        else:
            return last["id"]

    def populate(self, count=1, col="r", only_count_absent=False):
        base = self.newest() + 1

        for n in range(0,count):
            next_one = base + n
            print("[debug] populate :", n, base, next_one)

            if self.is_known_missing(next_one):
                print("[debug] known missing", next_one)
                continue

            tor = Torrent(next_one, self.db, self.config)
            self.members.append(tor)


    def generate_libgen_torrent_filename(self):
        name = (self.id ) * 1000
        return f"r_{name:03}.torrent"


    def is_known_missing(self, newest, col="r"):
        return newest *1000 in self.config["catalogue"]["r"]["known_missing"]


    def peer_exchange_m(self, info_hash_list):
        tracker_collection = Tracker_collection(self.db)

        all_tracker = tracker_collection.all()
        print("all tracker", all_tracker)
        print("all infohash", info_hash_list)
        #exit()

        scr = scraper.Scraper(
            timeout=5,
            infohashes=info_hash_list,
            trackers=all_tracker,
            #trackers=["udp//:tracker.opentrackr.org:1337"],
            )
        results = scr.scrape()

        print("xxx" * 100)
        for r in results:
            if isinstance(r,list):
                if len(r) == 1:
                    if r[0].startswith("Socket timeout for"):
                        print("just a timeout")
                        continue
                print("Unknow errro list:", r)
                exit()

            elif isinstance(r, dict):
                #print(r)
                print("######tracker")
                print(type(r["tracker"]))
                print(r["tracker"])

                #print("######result")
                #print(type(r["results"]))
                #print(r["results"])

                for rr in r["results"]:
                    print(rr)
                    ## TODO
                    ## 
                    ##
                    #update_torrent(**rr)

                #exit()
            else:
                print("unknown error type ", type(r), r)
                exit()

        exit()
        return results

    def peer_crawl(self, count=1, limit=60):
        print(f"this is a crawl party!!")
        for n in range(0,count):

            # TODO move limit to CONFIG
            oldest_n = self.db.torrent.find(order_by='chk_success_last', _limit=limit)

            oldest_n_ih = [ t["infohash"] for t in oldest_n ]
            print(oldest_n_ih)

            self.peer_exchange_m(oldest_n_ih)  ## TOTO RNAME


    def chk_for_new(self):
        pass

    def integrety_check_libgen(self):
        ### find out what torrents dont exists
        ### wirte missing to config toml?
        pass

