import requests
from collections import defaultdict
import libtorrent as lt
from pathlib import Path
from datetime import datetime
from parse import parse

from tracker import Tracker, Tracker_collection
from torrent import Torrent

from lib.ttsfix import scraper

#HTTP_GET_RETRY = 1  # move to config


class Torrent_collection:



    #TORRENT_DIR = dict(
    #        books = Path("data/torrent/books"), # get from config!
    #        scimag = Path("data/torrent/scimag"), # get from config!
    #        fiction = Path("data/torrent/fiction"), # get from config!
    #        )
    #
    ## TODO find out if httpS is okey
    #TORRENT_SRC = dict(
    #    books ="https://libgen.is/repository_torrent/",
    #    scimag = "https://gen.lib.rus.ec/scimag/repository_torrent/",
    #    fiction = "http://gen.lib.rus.ec/fiction/repository_torrent/" )
    #
    #TORRENT_MASK = dict(
    #        books="r_{}.torrent",
    #        ficton="f_{}.torrent",
    #        scimag="sm_{}-{}.torrent")
    #


    def __init__(self, db, config):
        self.db = db
        self.config = config
        #self.base_path = self.TORRENT_DIR
        #self.base_url = self.TORRENT_SRC
        self.members = self._load_all_from_db()


    def info(self):
        print("Info: ")
        for tor in self.members:
            print(tor)


    def _load_all_from_db(self):
        return [ tor for tor in self.db.torrent.find()]


    def newest(self, collection):
        last = self.db.torrent.find_one(order_by='-id', collection=collection)
        if last == None:
            return 0
        else:
            return last["id"]


    def populate(self, count=1, collection="books", only_count_absent=False):
        base = self.newest(collection) + 1

        for n in range(0,count):
            next_one = base + n
            #print("[debug] populate :", n, base, next_one)

            if self.is_known_missing(next_one, collection):
                print("[debug] known missing", next_one)
                continue

            tor = Torrent(next_one, collection, self.db, self.config)
            self.members.append(tor)


    #def generate_libgen_torrent_filename(self, collection):
    #    name = (self.id ) * 1000
    #    return f"r_{name:03}.torrent"


    def is_known_missing(self, newest, collection):
        return newest *1000 in self.config["catalogue"][collection]["known_missing"]


    def ensure_present(self, key, dictionary):
        if not "tracker" in dictionary.keys():
            print(f"[Debug] response dict has no key named {key}")
            return False
        return True


    def harvest_errors(self, part, timeouts):
        if isinstance(part, dict):
            error = part['error']
            print("error jdij: ", error)
            print(f"{type(error)}")
            exit()
            ## TODO, finish if needed

        else:
            # TODO: dont exit
            print(f"[Debug] unexpected type {type(part)} {part}")
            exit()


    def parse_response_result(self, results, maximas, timeouts):
        for r in results:
            if 'error' in r.keys():
                ### For now lets not care about this.
                ### It apearst these results are delivered back twice from the peer scraper lib
                ### so we can disregard this occurence

                #print("1" * 100, "ss")
                #print(r["infohash"], r["error"])
                #self.harvest_errors(r, timeouts)
                continue

            infohash = r["infohash"]
            seeders = r["seeders"]
            leechers = r["leechers"]
            completed = r["completed"]

            if infohash in maximas.keys():
                maximas[infohash]['seeders'] = max(seeders, maximas[infohash]['seeders'])
                maximas[infohash]['leechers'] = max(leechers, maximas[infohash]['leechers'])
                maximas[infohash]['completed'] = max(completed, maximas[infohash]['completed'])

            else:
                r.pop("infohash")
                maximas[infohash] = r


    def parse_response_dict(self, part, timeouts, maximas, successful_trackers):
        if not self.ensure_present('tracker', part):
            # TODO
            # if tracker and result -> mark tarcker as success
            # dont exit but log error and continue
            print("[DEBUG] bad bad bad")
            exit()

        if self.ensure_present('results', part):
            if isinstance( part['results'], str):
                # TODO: dont exit, just log..
                print("[Debug] part['results'], part[results]")
                self.harvest_errors(part, timeouts)
                exit()

            if isinstance( part['results'][0], str):
                if self.is_timeout(part['results'][0]):
                    #timeouts.extend(self.parse_timeout(part['results'][0]))
                    timeouts.append(self.parse_timeout(part['results'][0]))
                else:
                    # Todo: dont exit..
                    print("[Debug] unknown error")
                    exit()

            else:
                # at this point we can assume a trackers response successfull
                successful_trackers.add(part['tracker'])
                self.parse_response_result(part['results'], maximas, timeouts)

        else:
            # TODO dont exit
            print("[debug] also not impemented" * 100, part)
            exit()

        return

    def parse_response_list(self, part, timeouts):
        for p in part:
            if not isinstance(p, str):
                # TODO: dont exit
                print(f"Type error in response: {p}. Expecting string got {type(p)}.")
                exit()
            if self.is_timeout(p):
                timeouts.append(self.parse_timeout(p))
                #timeouts.extend(self.parse_timeout(p))
            else:
                """
                Unknown error in response: Connection refused for tracker.coppersurfer.tk:6969: [Errno 111] Connection refused. Expeting timeout"""
                print(f"Unknown error in response: {p}. Expeting timeout")

        return


    def is_timeout(self, string):
        return string.startswith("Socket timeout for")


    def parse_timeout(self, timeout, proto="udp"):
        mask = "Socket timeout for {}: timed out"
        udp_mask = "udp://{}/announce"
        #print("DEBUG PARSING: ", timeout)
        return udp_mask.format(parse(mask, timeout)[0])


    def parse_tracker_response(self, response):
        #print("Results: ", response)
        timeouts = []
        maximas = dict()
        successful_trackers = set()

        for part in response:
            if isinstance(part, dict):
                self.parse_response_dict(part, timeouts, maximas, successful_trackers)
            elif isinstance(part, list):
                self.parse_response_list(part, timeouts)
            else:
                print(f"[Debug] part of response is neither dict nore list: {type(part)}")

        return maximas, timeouts, successful_trackers


    def save_result(self, max_results, timeouts, successful_trackers):

        # TODO:
        #   * calculate what torrents failed at updating
        #       * we can do this by comparing the questions and the answers
        #       * update timestamp and fail count on fail

        print("timeouts: ",timeouts)
        print("successful_trackers: ",successful_trackers)

        successful_and_timeout = set(successful_trackers) & set(timeouts)
        if successful_and_timeout:
            print("successful_and_timeout: ", successful_and_timeout)
            print("[Debug] so much confusion. But could be okey")
            exit()


        for trackername in successful_trackers:
            tracker = Tracker(self.db, trackername)
            tracker.increment_success_count()

        for trackername in timeouts:
            tracker = Tracker(self.db, trackername)
            tracker.increment_fail_count()


        # TODO: profile the update function to see if switching to update_many is relevant
        #       updated_many = self.db.torrent.update_many(max_results, ['infohash'])

        # TODO: make this oo! see tracker..
        for res in max_results:
            res["chk_success_last"] = datetime.utcnow()
            res["chk_success_count"] = 1 + self.db.torrent.find_one(infohash=res["infohash"])["chk_success_count"]
            self.db.torrent.update(res, ['infohash'], return_count=True, ensure=False )



    def peer_exchange_m(self, info_hash_list):
        tracker_collection = Tracker_collection(self.db)
        all_tracker = tracker_collection.all()
        udp_tracker = [ tracker for tracker in all_tracker if tracker.startswith("udp") ]

        #TODO: do we also want to use not UDP tackers?
        # other_tracker = set(all_tracker) - set(udp_tracker)
        #
        loglevel = self.config["peersearch"]["scraper_loglevel"]

        scr = scraper.Scraper(
            loglevel=loglevel,
            timeout=5,
            infohashes=info_hash_list,
            trackers=udp_tracker,
            )

        results = scr.scrape()
        maximas, timeouts, successful_trackers = self.parse_tracker_response(results)
        maximas_lst = self.unscramble( maximas)
        successful_trackers = self.clean_tracker_url(successful_trackers, add_postfix=True)
        self.save_result(maximas_lst, timeouts, successful_trackers)


    def unscramble(self, maximas):
        """ we get several list of dictinaries containig or results from the scraper
            yet to comapre these efficnetly, we need to have a dict of dicts
        """
        maximas_lst = []
        for k, v in maximas.items():
            v["infohash"] = k
            maximas_lst.append(v)
        return maximas_lst


    def clean_tracker_url(self, trackers, add_postfix=False):
        """ libtorrent seems to use "udp://" while the torrent files
            use the notation "udp//:

            all observed tracker have the postfix '/announce'
            we get them wo/ the prefix from the scraper
            set add_postfix to True to add
        """
        POSTFIX = "/announce"
        if add_postfix:
            trackers = [t + POSTFIX for t in trackers]
        return [t.replace("udp//:", "udp://") for t in trackers]

    def peer_crawl(self, count=1):
        for n in range(0,count):
            limit = self.config["peersearch"]["udp_batchsize"]
            oldest_n = self.db.torrent.find(order_by='chk_success_last', _limit=limit)
            oldest_n_ih = [ t["infohash"] for t in oldest_n ]
            #print(oldest_n_ih)
            self.peer_exchange_m(oldest_n_ih)  ## TOTO RNAME


    def chk_for_new(self):
        pass

    def integrety_check_libgen(self):
        # TODO: find out what torrents dont exists in db
        pass

