import requests
from collections import defaultdict
import libtorrent as lt
from pathlib import Path
from datetime import datetime
from parse import parse

from tracker import Tracker, Tracker_collection
from torrent import Torrent

from lib.ttsfix import scraper
#from lib.ttsfix import scraper


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


    def is_str_timeout(self, msg):
        if isinstance(msg, str):
            if msg.startswith("Socket timeout for"):
                print("[Debug] just a timeout")
                return True
            else:
                print("[Debug] is not timeout")
                return False
        else:
            print("[Debug] Is not str")
            return False


    def is_list_with_only_timeout(self, msg):
        if isinstance(msg,list):
            if len(msg) == 1:
                if self.is_str_timeout(msg[0]):
                    return True
                print("[Debug] is list with only one memebr but not 'Socket timeout for..'")
            print("[Debug] is list but more than 1 members")
        return False


    def ensure_present(self, key, dictionary):
        if not "tracker" in dictionary.keys():
            print(f"response dict has no key named {key}")
            return False
        return True


    def harvest_errors(self, part, timeouts):
        print("NOT implemented yet" )
        print(part)
        print("NOT implemented yet" )


    def parse_response_result(self, results, maximas):
        ## TODO, this is extreemly unperfomant code... 
        ## we should put this in a dict..
        print("results" * 100, results)
        #exit()
        for m in maxima:
            if m["infohash"] == results["infohash"]:
                pass
            break
        else:
            maximas.append(results)



        print()

    def parse_response_dict(self, part, timeouts, maximas):
        print("parsing dict", part)
        if not self.ensure_present('tracker', part):
            # TODO
            # if tracker and result -> mark tarcker as success
            exit()
        if self.ensure_present('results', part):
            self.parse_response_result(part['results'], maximas)
            exit()
            # maybe just return, not exit or parse the error dict?
        if self.ensure_present('errors', part):
            print("part: ", part)
            self.harvest_errors(part, timeouts)
        else:
            print("also not impemented" * 100)
            exit()
        ## TODO: look for other things in this dicst?


        # if has tracker and has results 
        return

    def parse_response_list(self, part, timeouts):
        #print("list:",part)
        for p in part:
            if not isinstance(p, str):
                raise(f"Type error in response: {p}. Expecting string got {type(p)}.")
            if self.is_timeout(p):
                timeouts.append(self.parse_timeout(p))
            else:
                raise("Unknown error in response: {p}. Expeting timeout")
        return


    def is_timeout(self, string):
        return string.startswith("Socket timeout for")


    def parse_timeout(self, timeout, proto="udp"):
        mask = "Socket timeout for {}: timed out"
        udp_mask = "udp://{}/announce"
        return udp_mask.format(parse(mask, timeout)[0])


    def parse_timeoutSSS(self, timeouts):
        mask = "Socket timeout for {}: timed out"
        udp_mask = "udp://{}/announce"
        print("timeouts", timeouts)
        return [ udp_mask.format(parse(mask, t)[0]) for t in timeouts]


    def parse_tracker_response(self, response):
        print("Results: ", response)
        timeouts = []
        maximas = []

        for part in response:
            if isinstance(part, dict):
                print("dict")
                self.parse_response_dict(part, timeouts, maximas)
            elif isinstance(part, list):
                print("list")
                self.parse_response_list(part, timeouts)
            else:
                print("other")

        print("timeouts: ", timeouts)
        exit()
        return timeouts, ...


    def parse_tracker_response_(self, results):
        # data is a bit messy
        # we can get a list with errors
        # or a dict with a dict of erros
        # or a dict with list of real_results, we only want this

        #max_seed = defaultdict(int)
        #max_leech = defaultdict(int)
        timeouts = []

        # TODO, change exit to rais
        print("results:",results)
        exit()
        max_results = []

        # TODO TODO TODO
        for r in results:
            this = dict()
            seed_max = 0
            leech_max = 0
            infohash = ""


            if self.is_list_with_only_timeout(r):
                timeouts.append(r[0])
                continue

            elif isinstance(r, dict):
                if isinstance(r["results"], dict):
                    if self.is_list_with_only_timeout(r["results"]):
                        continue
                    print("[Error] what the fuck is this a dict?")
                    exit()
                if not isinstance(r["results"], list):
                    print("[Error] this should not happen. r['results'] is not list not error dict")
                    print("r['results']:::",r['results'])
                    exit()

            if True:
                for rr in r["results"]:
                    if isinstance(rr, str):
                        if self.is_str_timeout(rr):
                            print("Debug: got rid of timout")
                            timeouts.append(rr)
                            continue
                    if not 'seeders' in rr.keys():
                        print("[debug] no seeders found in result dict")
                        continue

                    print("rr:",rr)
                    infohash = rr["infohash"]
                    seed_max = max(rr["seeders"], seed_max)
                    leech_max = max(rr["leechers"], leech_max)

            # TODO: find out if this makes any sense at all... 
            # should this be indented one level further?
            #
            if True:
                if infohash:
                    max_results.append(dict(infohash=infohash,
                                        seed_count=seed_max,
                                        leech_count=leech_max,
                                        chk_success_last=datetime.utcnow()))

            #else:
            #    print("[Debug] unknown error type ", type(r), r)
            #    exit()

        print(max_results, "x" * 100, timeouts)
        return max_results, timeouts


    def save_result(self, max_results, timeouts):
        # we know that all torrents WO/ that have no results
        # but were in tha batch are failures
        # TODO, update timstamp and fail count
        #
        # we also know all tracker wo/ results are to be considered fails


        timeouts = self.parse_timeout(timeouts)
        print(timeouts)
        ## TODO save timouts

        print("max_results: ",max_results)
        #print("dddddd")

        ### TODO; increment the update counter!
        for res in max_results:
            #print("tyype res", type(res))
            #print(res, res["infohash"])
            res["chk_success_count"] = self.db.torrent.find_one(infohash=res["infohash"])["chk_success_count"]
            updated_many = self.db.torrent.update(res, ['infohash'], return_count=True )
            print("Updateing", res)
            # TODO check if update_many == 1, else error
            print("updte many:", updated_many)


        import time
        time.sleep(10)
        ## TODO: proile the update to see if switching to update_many is relevant
        #updated_many = self.db.torrent.update_many(max_results, ['infohash'])

        #print(f"[debug] {updated} rows updated")
        exit()


    def peer_exchange_m(self, info_hash_list):
        tracker_collection = Tracker_collection(self.db)
        all_tracker = tracker_collection.all()
        udp_tracker = [ tracker for tracker in all_tracker if tracker.startswith("udp") ]

        # keep this
        #other_tracker = set(all_tracker) - set(udp_tracker)

        print("all tracker", all_tracker)
        print("all infohash", info_hash_list)
        #exit()

        scr = scraper.Scraper(
            timeout=5,
            infohashes=info_hash_list,
            trackers=udp_tracker,
            #trackers=other_tracker,
            )
        results = scr.scrape()
        max_results, timeouts = self.parse_tracker_response(results)

        #print("timeouts:", timeouts)
        # push results to db..
        ## {hashinfo:"foo", seed_count:99, leech_count:9}

        self.save_result(max_results, timeouts)

        exit()


    def peer_crawl(self, count=1, limit=60):
        print(f"this is a crawl party!!")
        for n in range(0,count):

            # TODO move limit to CONFIG
            oldest_n = self.db.torrent.find(order_by='-chk_success_last', _limit=limit)

            oldest_n_ih = [ t["infohash"] for t in oldest_n ]
            print(oldest_n_ih)

            self.peer_exchange_m(oldest_n_ih)  ## TOTO RNAME


    def chk_for_new(self):
        pass

    def integrety_check_libgen(self):
        ### find out what torrents dont exists
        ### wirte missing to config toml?
        pass

