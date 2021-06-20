import requests
import libtorrent as lt
from pathlib import Path
from datetime import datetime
from lib.ttsfix import scraper

from tracker import Tracker, Tracker_collection

from lib.ttsfix import scraper


HTTP_GET_RETRY = 1  # move to config

class Torrent:
    #TORRENT_DIR = Path("data/torrent") # get from config!
    #TORRENT_SRC = "https://libgen.is/repository_torrent/"



    ### TODO: Move to config
    TORRENT_DIR = dict(
            books = Path("data/torrent/books"), # get from config!
            scimag = Path("data/torrent/scimag"), # get from config!
            fiction = Path("data/torrent/fiction"), # get from config!
            )

    TORRENT_SRC = dict(
        books ="https://libgen.is/repository_torrent/",
        scimag = "http://gen.lib.rus.ec/scimag/repository_torrent/",
        fiction = "http://gen.lib.rus.ec/fiction/repository_torrent/" )

    TORRENT_MASK = dict(
            books="r_{}.torrent",
            ficton="f_{}.torrent",
            scimag="sm_{}-{}.torrent")




    def __init__(self, id, collection, db, config):
        self.db = db
        #self.tracker_db = db.tracker
        #self.torrent_db = db.torrent
        #self.log_db = db.log

        self.config = config
        self.id = id
        self.collection = collection
        #assert collection in ["books", "scimag", "fictoin"]

        self.file_name = self.generate_libgen_torrent_filename()
        self.full_path = self.TORRENT_DIR[collection] / self.file_name
        self.url = self.TORRENT_SRC[collection] + self.file_name

        tor = self.db.torrent.find_one(file_name=self.file_name)
        if not tor:
            #print(f"[debug] obj does NOT exits in db")
            self.get_from_file()
            self.save_to_db()
            tor = self.db.torrent.find_one(file_name=self.file_name)

        self.infohash = tor["infohash"]
        #self.collection = self.collection
        self.seeders = tor["seeders"]
        self.leechers = tor["leechers"]
        self.completed = tor["completed"]
        self.creation_date = tor["creation_date"]
        self.size_bytes = tor["size_bytes"]
        self.chk_fail_last = tor["chk_fail_last"]
        self.chk_fail_count = tor["chk_fail_count"]
        self.chk_success_last = tor["chk_success_last"]
        self.chk_success_count = tor["chk_success_count"]

        ## TODO: do we need to save this now?


    def info(self):
        print(f"Info on torrent: {self.file_name}")
        print(f"    infohash:                {self.infohash}")
        print(f"    collection:              {self.collection}")
        print(f"    seeders:                 {self.seeders}")
        print(f"    leechers:                {self.leechers}")
        print(f"    completed:               {self.completed}")
        print(f"    id:                      {self.id}")
        print(f"    creation_date:           {self.creation_date}")
        print(f"    full_path:               {self.full_path}")
        print(f"    url:                     {self.url}")
        print(f"    size_bytes:              {self.size_bytes}")
        print(f"    chk_fail_last:           {self.chk_fail_last}")
        print(f"    chk_fail_count:          {self.chk_fail_count}")
        print(f"    chk_success_last:        {self.chk_success_last}")
        print(f"    chk_success_count:       {self.chk_success_count}")


    def generate_libgen_torrent_filename(self):
        ## TODO get this mask from config
        ##      use format() i guess..

        name = (self.id ) * 1000
        if self.collection == "books":
            return f"r_{name:03}.torrent"

        elif self.collection == "fiction":
            ### handle this small inconsistency
            if name:
                return f"f_{name:03}.torrent"
            return "f_0.torrent"

        elif self.collection == "scimag":
            name = name * 100
            name_to = name + 99999
            #print(name, name_to)
            #exit()
            return f"sm_{name:08}-{name_to:08}.torrent"
        else:
            print("[Debug] unknown collection")
            exit()


    def get_http(self):
        # returns: Request obj, Retry, Success
        try:
            r = requests.get(self.url)
            if r.status_code == 200:
                return r, False, True
            if r.status_code == 404:
                print(f"Possible missing torrent detected: {self.id}")
                self.db.log.insert(dict(name=self.file_name,
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
        ### TODO:
        ### think about if we want to add a collection colum for tracker
        #print("[i] adding trackers if new ones found")

        tracker_in_torrent = set(self.get_tracker(ti))
        tracker_in_db = set([t["url"] for t in self.db.tracker.find()])
        tracker_new = tracker_in_torrent - tracker_in_db

        if len(tracker_new) == 0:
            return

        print(f"[+] Adding {len(tracker_new)} new tracker")
        for url in tracker_new:
            #print(f"[debug] insertring: {name}")
            """
            self.db.tracker.insert(dict(url=url,
                                chk_success_count=0,
                                chk_success_last=None,
                                chk_fail_count=0,
                                chk_fail_last=None,
                                ))
            """
            #print("URL", url)
            tracker = Tracker(self.db, url)

        self.db.log.insert(dict(name=self.file_name,
            status=f"added trackers: {len(tracker_new)}",
                        datetime=datetime.utcnow()))


    def get_tracker(self, ti):
        return [t.url for t in ti.trackers()]


    def save_to_db(self):
        print(f'[+] Saving new torrent to DB from file {self.full_path} ')
        ti = lt.torrent_info(str(self.full_path))
        creation_date = ti.creation_date()
        self.process_tracker(ti)
        infohash = str(ti.info_hashes().get_best())
        size_bytes = ti.total_size()
        self.db.torrent.insert(dict(file_name=self.file_name,
                            id=self.id,
                            collection = self.collection,
                            infohash = infohash,
                            size_bytes = size_bytes,
                            creation_date = creation_date,
                            chk_fail_count = 0,
                            chk_fail_last = None,
                            chk_success_count = 0,
                            chk_success_last = None,
                            completed = None,
                            #leecher = None, # TODO hmmm why do we not need this?
                            #seeder = None,
                            ))

        #new_tracker = [e.url for e in ti.trackers()]
        #trackers.update_ignore()

        self.db.log.insert(dict(name=self.file_name,
                        status=f"added torrent {self.id}",
                        datetime=datetime.utcnow()))

