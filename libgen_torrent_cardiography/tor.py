#import toml
#import dataset
import requests
import libtorrent as lt
from pathlib import Path
from datetime import datetime
from lib.ttsfix import scraper

from tracker import Tracker

from lib.ttsfix import scraper

#CONFIG = "mgmt.toml"

#TORRENT_DIR = Path("data/torrent")
#TORRENT_SRC = "https://libgen.is/repository_torrent/"

#db = dataset.connect('sqlite:///data/ltc.sqlite')

HTTP_GET_RETRY = 1

#tracker = db['tracker']
#torrent = db['torrent']
#log = db['log']

# Active record pattern
class Tor:
    TORRENT_DIR = Path("data/torrent") # get from config!
    TORRENT_SRC = "https://libgen.is/repository_torrent/"

    def __init__(self, id, db, config):
        self.db = db
        self.tracker = db['tracker']
        self.torrent = db['torrent']
        self.log = db['log']
        self.config = config

        self.id = id

        self.file_name = self.generate_libgen_torrent_filename()
        self.full_path = self.TORRENT_DIR / self.file_name
        self.url = self.TORRENT_SRC + self.file_name

        ## lets check if exists in db. if not create?
        #print("file_name", self.file_name)

        tor = self.torrent.find_one(file_name=self.file_name)

        #if tor:
        #    print(f"[debug] obj exits in db")

        if not tor:
            print(f"[debug] obj does NOT exits in db")
            self.get_from_file()
            self.save_to_db()
            tor = self.torrent.find_one(file_name=self.file_name)

            #print("saved thing is now", tor)

        self.infohash = tor["infohash"]
        self.seed_count = tor["seed_count"]
        self.chk_fail_last = tor["chk_fail_last"]
        self.chk_fail_count = tor["chk_fail_count"]
        self.chk_success_last = tor["chk_success_last"]
        self.chk_success_count = tor["chk_success_count"]

        #self._fetch(self)
        #self._process(self)

    def info(self):
        print(f"Info on torrent: {self.file_name}")
        print(f"    infohash:                {self.infohash}")
        print(f"    seed_count:              {self.seed_count}")
        print(f"    id:                      {self.id}")
        print(f"    full_path:               {self.full_path}")
        print(f"    url:                     {self.url}")
        print(f"    chk_fail_last:           {self.chk_fail_last}")
        print(f"    chk_fail_count:          {self.chk_fail_count}")
        print(f"    chk_success_last:        {self.chk_success_last}")
        print(f"    chk_success_count:       {self.chk_success_count}")

    @staticmethod
    def newest(db):
        #last = torrent.find_one(order_by='-file_name')
        last = db["torrent"].find_one(order_by='-id')
        if last == None:
            return 0
        else:
            return last["id"]

    @staticmethod
    def populate(db, config, count=1, col="r", only_count_absent=False):
        base = Tor.newest(db)
        for n in range(0,count):
            next_one = base + n
            print("[debug] populate :", n, base, next_one)

            if Tor.is_known_missing(next_one, config):
                print("[debug] known missing", next_one)
                continue

            new_tor = Tor(next_one, db, config)

            #if new_tor.exists_in_db:
            #    print(f"Found {new_tor.id} in db. Skipping")
            #    continue
            #
            #print(f"[debug] Did not find {new_tor.id} in db")
            #new_tor.get_from_file()
            #new_tor.save()

    def generate_libgen_torrent_filename(self):
        name = (self.id ) * 1000
        return f"r_{name:03}.torrent"

    def get_http(self):
        # returns: Request obj, Retry, Success
        try:
            r = requests.get(self.url)
            if r.status_code == 200:
                return r, False, True
            if r.status_code == 404:
                print(f"Possible missing torrent detected: {self.id}")
                log.insert(dict(name=self.file_name,
                                status=f"Possible missing torrent detected: {self.id}",
                                datetime=datetime.utcnow()))
                return r, False, False
            return None, True, False
        except requests.exceptions.HTTPError as errh:
            print("[GET_HTTP] Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print("[GET_HTTP] Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print("[GET_HTTP] Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print("[GET_HTTP] Total failure",err)
        return None, True, False


    def get_from_file(self):
        if self.full_path.is_file():
            print(f"[debug] found f{self.full_path} in dir")
            return 'found'

        for e in range(HTTP_GET_RETRY+1):
            r, retry, success = self.get_http()
            if retry == False:
                break

        if not success:
            exit(f"[e] Failed to fetch torrent file form url: {self.url}")

        with open(self.full_path, 'wb') as torrent_out:
            torrent_out.write(r.content)
        print(f"[+] file {self.id} fetched and writen ({self.url})")


    def process_tracker(self, ti):
        #print("[i] adding trackers if new ones found")
        tracker_in_torrent = set(self.get_tracker(ti))
        tracker_in_db = set([t["name"] for t in self.tracker.find()])
        tracker_new = tracker_in_torrent - tracker_in_db

        if len(tracker_new) == 0:
            return

        print(f"[+] Adding {len(tracker_new)} new tracker")
        for name in tracker_new:
            #print(f"[debug] insertring: {name}")
            self.tracker.insert(dict(name=name,
                                chk_success_count=0,
                                chk_success_last=None,
                                chk_fail_count=0,
                                chk_fail_last=None,
                                ))
        log.insert(dict(name=self.file_name,
            status=f"added trackers: {len(tracker_new)}",
                        datetime=datetime.utcnow()))


    def get_tracker(self, ti):
        return [t.url for t in ti.trackers()]


    def load(self):
        ### load if exists, else creat new?!
        #tor = torrent.findone(id=["self.id"])
        tor = self.torrent.findone(id=["self.filename"])
        if tor == None: ## ugly!
            # create new
            pass # TODO
        else:
            print("ihihiihihihi", tor["infohash"])


    ##### TODO TODO TODO TODO 
    ##### TODO TODO TODO TODO 
    def save_to_db(self):
        print(f'[+] Saving new torrent to DB from file {self.full_path} ')
        ti = lt.torrent_info(str(self.full_path))

        self.process_tracker(ti)

        infohash = str(ti.info_hashes().get_best())
        self.torrent.insert(dict(file_name=self.file_name,
                            id=self.id,
                            infohash = infohash,
                            chk_fail_count = 0,
                            chk_fail_last = None,
                            chk_success_count = 0,
                            chk_success_last = None,
                            ))

        #new_tracker = [e.url for e in ti.trackers()]
        #trackers.update_ignore()

        self.log.insert(dict(name=self.file_name,
                        status=f"added torrent {self.id}",
                        datetime=datetime.utcnow()))

    @staticmethod
    def is_known_missing( newest, config, col="r"):
        ### TOFIX
        newest -= 1
        newest += 1
        return newest *1000 in config["catalogue"]["r"]["known_missing"]


    def peer_exchange(self):

        ### apparently we can pass multiple infohashes in one go... 
        ### Up to about 74 torrents can be scraped at once. A full scrape can't be done with this protocol.

        all_tracker = Tracker.all(self.db)
        print(f"all tracker: {all_tracker}")

        scr = scraper.Scraper(
            timeout=2,
            infohashes=[self.infohash,],
            trackers=all_tracker,
            #trackers=["udp//:tracker.opentrackr.org:1337"],
            )
        results = scr.scrape()
        print(results)
        return results


    @staticmethod
    def peer_exchange_m(db, info_hash_list):
        all_tracker = Tracker.all(db)
        print(f"all tracker: {all_tracker}")
        scr = scraper.Scraper(
            timeout=2,
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

                print("######result")
                print(type(r["results"]))
                print(r["results"])

                for rr in r["results"]:
                    print(rr)
                    ## TODO
                    ## 
                    ##
                    #update_torrent(**rr)

                    for e 
                exit()
            else:
                print("unknown error type ", type(r), r)
                exit()

        exit()
        return results

        

    @staticmethod
    def peer_crawl(db, config, count=1):
        print(f"this is a crawl party!!")
        for n in range(0,count):


            #oldest = db["torrent"].find(order_by='chk_success_last').__next__() # maybe -chk..

            ## obj
            oldest = db["torrent"].find_one(order_by='chk_success_last')
            
            ## list
            oldest_n = db["torrent"].find(order_by='chk_success_last', _limit=60)
            oldest_n_ih = [ t["infohash"] for t in oldest_n ]
            print(oldest_n_ih)

            #Tor.peer_exchange()
            Tor.peer_exchange_m(db, oldest_n_ih)  ## TOTO RNAME

            #print(oldest["id"], oldest["infohash"])
            #tor = Tor(oldest["id"], db, config)

            #tor.peer_exchange_m(oldes_n_ih)  ## TOTO RNAME

            # get least fresh torrent
            # try to fetch peer info
            # save peer info and update stats
            # move to next

    def chk_seeds():
        pass
    def least_fresh():
        pass
    def chk_fornew():
        pass

    def integrety_check_libgen(self):
        ### find out what torrents dont exists
        ### wirte missing to config toml?
        pass

