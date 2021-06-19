import requests
import libtorrent as lt
from pathlib import Path
from datetime import datetime
from lib.ttsfix import scraper

from tracker import Tracker, Tracker_collection

from lib.ttsfix import scraper


HTTP_GET_RETRY = 1  # move to config

class Torrent:
    TORRENT_DIR = Path("data/torrent") # get from config!
    TORRENT_SRC = "https://libgen.is/repository_torrent/"

    def __init__(self, id, db, config):
        self.db = db
        #self.tracker_db = db.tracker
        #self.torrent_db = db.torrent
        #self.log_db = db.log

        self.config = config
        self.id = id

        self.file_name = self.generate_libgen_torrent_filename()
        self.full_path = self.TORRENT_DIR / self.file_name
        self.url = self.TORRENT_SRC + self.file_name

        tor = self.db.torrent.find_one(file_name=self.file_name)
        if not tor:
            #print(f"[debug] obj does NOT exits in db")
            self.get_from_file()
            self.save_to_db()
            tor = self.db.torrent.find_one(file_name=self.file_name)

        self.infohash = tor["infohash"]
        self.seeders = tor["seeders"]
        self.leechers = tor["leechers"]
        self.chk_fail_last = tor["chk_fail_last"]
        self.chk_fail_count = tor["chk_fail_count"]
        self.chk_success_last = tor["chk_success_last"]
        self.chk_success_count = tor["chk_success_count"]


    def info(self):
        print(f"Info on torrent: {self.file_name}")
        print(f"    infohash:                {self.infohash}")
        print(f"    seeders:                 {self.seeders}")
        print(f"    leechers:                {self.leechers}")
        print(f"    id:                      {self.id}")
        print(f"    full_path:               {self.full_path}")
        print(f"    url:                     {self.url}")
        print(f"    chk_fail_last:           {self.chk_fail_last}")
        print(f"    chk_fail_count:          {self.chk_fail_count}")
        print(f"    chk_success_last:        {self.chk_success_last}")
        print(f"    chk_success_count:       {self.chk_success_count}")


    ##  TODO decide where this should luve
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
            #print(f"[debug] found f{self.full_path} in dir")
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
        tracker_in_db = set([t["name"] for t in self.db.tracker.find()])
        tracker_new = tracker_in_torrent - tracker_in_db

        if len(tracker_new) == 0:
            return

        print(f"[+] Adding {len(tracker_new)} new tracker")
        for name in tracker_new:
            #print(f"[debug] insertring: {name}")
            self.db.tracker.insert(dict(name=name,
                                chk_success_count=0,
                                chk_success_last=None,
                                chk_fail_count=0,
                                chk_fail_last=None,
                                ))
        self.db.log.insert(dict(name=self.file_name,
            status=f"added trackers: {len(tracker_new)}",
                        datetime=datetime.utcnow()))


    def get_tracker(self, ti):
        return [t.url for t in ti.trackers()]

    """
    def load(self):
        ### load if exists, else creat new?!
        #tor = torrent.findone(id=["self.id"])
        tor = self.db.torrent.findone(id=["self.filename"])
        if tor == None: ## ugly!
            # create new
            pass # TODO
        else:
            print("ihihiihihihi", tor["infohash"])
    """


    def save_to_db(self):
        print(f'[+] Saving new torrent to DB from file {self.full_path} ')
        ti = lt.torrent_info(str(self.full_path))

        self.process_tracker(ti)

        infohash = str(ti.info_hashes().get_best())
        self.db.torrent.insert(dict(file_name=self.file_name,
                            id=self.id,
                            infohash = infohash,
                            chk_fail_count = 0,
                            chk_fail_last = None,
                            chk_success_count = 0,
                            chk_success_last = None,
                            ))

        #new_tracker = [e.url for e in ti.trackers()]
        #trackers.update_ignore()

        self.db.log.insert(dict(name=self.file_name,
                        status=f"added torrent {self.id}",
                        datetime=datetime.utcnow()))


    """
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
    """
