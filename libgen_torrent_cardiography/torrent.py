import requests
import libtorrent as lt
from pathlib import Path
from datetime import datetime
from lib.ttsfix import scraper

from tracker import Tracker, Tracker_collection
from lib.ttsfix import scraper



class Torrent:


    # TODO, replace id with infohash, if possible
    def __init__(self, id, collection, db, config):
    #def __init__(self, infohash, collection, db, config):

        self.db = db
        self.id = id
        self.collection = collection

        self.config = config
        assert collection in ["books", "scimag", "fiction"]


        self.HTTP_GET_RETRY = self.config["torrent_fetch"]["http_get_retry"]
        self.file_name = self.generate_libgen_torrent_filename()

        self.full_path = Path(self.config["catalogue"][self.collection]["dir"]) / self.file_name
        #self.url = self.config["catalogue"][self.collection]["base_url"] + self.file_name
        self.url = self.generate_url()


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
        self.dht_peers = tor["dht_peers"]
        self.creation_date = tor["creation_date"]
        self.size_bytes = tor["size_bytes"]

        self.scrape_fail_last = tor["scrape_fail_last"]
        self.scrape_fail_count = tor["scrape_fail_count"]
        self.scrape_success_last = tor["scrape_success_last"]
        self.scrape_success_count = tor["scrape_success_count"]

        self.dht_fail_last = tor["dht_fail_last"]
        self.dht_fail_count = tor["dht_fail_count"]
        self.dht_success_last = tor["dht_success_last"]
        self.dht_success_count = tor["dht_success_count"]


    def info(self):
        print(f"Info on torrent: {self.file_name}")
        print(f"    infohash:                {self.infohash}")
        print(f"    collection:              {self.collection}")
        print(f"    seeders:                 {self.seeders}")
        print(f"    leechers:                {self.leechers}")
        print(f"    completed:               {self.completed}")
        print(f"    dht_peers:               {self.dht_peers}")
        print(f"    id:                      {self.id}")
        print(f"    creation_date:           {self.creation_date}")
        print(f"    full_path:               {self.full_path}")
        print(f"    url:                     {self.url}")
        print(f"    size_bytes:              {self.size_bytes}")
        print(f"    scrape_fail_last:        {self.scrape_fail_last}")
        print(f"    scrape_fail_count:       {self.scrape_fail_count}")
        print(f"    scrape_success_last:     {self.scrape_success_last}")
        print(f"    scrape_success_count     {self.scrape_success_count}")
        print(f"    dht_fail_last:           {self.dht_fail_last}")
        print(f"    dht_fail_count:          {self.dht_fail_count}")
        print(f"    dht_success_last:        {self.dht_success_last}")
        print(f"    dht_success_count:       {self.dht_success_count}")



    def generate_url(self):
        return self.config["catalogue"][self.collection]["base_url"] + self.file_name


    def generate_libgen_torrent_filename(self):
        ## TODO get this mask from config
        ##      use format() i guess..

        name = (self.id ) * 1000
        if self.collection == "books":

            return self.config["catalogue"][self.collection]["file_mask"].format(name)


        elif self.collection == "fiction":
            ### handle this small inconsistency
            if name:

                return self.config["catalogue"][self.collection]["file_mask"].format(name)

            return "f_0.torrent"

        elif self.collection == "scimag":
            name = name * 100
            name_to = name + 99999

            return self.config["catalogue"][self.collection]["file_mask"].format(name, name_to)

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

        for e in range(self.HTTP_GET_RETRY+1):
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
            tracker = Tracker(self.db, url)

        self.db.log.insert(dict(name=self.file_name,
            status=f"added trackers: {len(tracker_new)}",
                        datetime=datetime.utcnow()))


    def get_tracker(self, ti):
        return [t.url for t in ti.trackers()]


    def save_to_db(self):
        ### TODO find out if we really need this block ???? :D
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
                            dht_peers = 0,
                            dht_fail_count = 0,
                            dht_fail_last = None,
                            dht_success_count = 0,
                            dht_success_last = None,
                            scrape_fail_count = 0,
                            scrape_fail_last = None,
                            scrape_success_count = 0,
                            scrape_success_last = None,
                            completed = None,
                            #leecher = None, # TODO hmmm why do we not need this?
                            #seeder = None,
                            ))

        #new_tracker = [e.url for e in ti.trackers()]
        #trackers.update_ignore()

        self.db.log.insert(dict(name=self.file_name,
                        status=f"added torrent {self.id}",
                        datetime=datetime.utcnow()))

