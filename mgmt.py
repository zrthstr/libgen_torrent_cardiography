
# find first missing torrent
# fetch & save file in dir
# read data & store:
#   tracker info
#   torrent info
#
#
#   todo:
#   * add uniqe and primary key for torrents and tracker

import toml
import dataset
import requests
import libtorrent as lt
from pathlib import Path
from datetime import datetime

CONFIG = "mgmt.toml"

#TORRENT_DIR = Path("data/torrent")
#TORRENT_SRC = "https://libgen.is/repository_torrent/"

db = dataset.connect('sqlite:///data/ltc.sqlite')

HTTP_GET_RETRY = 1

tracker = db['tracker']
torrent = db['torrent']
log = db['log']

# Active record pattern
class Tor:
    TORRENT_DIR = Path("data/torrent") # get from config!
    TORRENT_SRC = "https://libgen.is/repository_torrent/"

    def __init__(self, id):
        self.id = id

        self.file_name = self.generate_libgen_torrent_filename()
        self.full_path = self.TORRENT_DIR / self.file_name
        self.url = self.TORRENT_SRC + self.file_name

        ## lets check if exists in db. if not create?
        print("file_name", self.file_name)
        ttt = torrent.find_one(file_name=self.file_name)
        if ttt:
            # EXISTS! lets load  TODO Rename ttt
            print(ttt)
            self.infohash = ttt["infohash"]
            self.seed_count = ttt["seed_count"]
            self.chk_fail_last = ttt["chk_fail_last"]
            self.chk_fail_count = ttt["chk_fail_count"]
            self.chk_success_last = ttt["chk_success_last"]
            self.chk_success_count = ttt["chk_success_count"]


        else:
            ## DOESNT EXCIST! lets create new
            self.get_from_file()
            self.save_to_db()
            ### NOW load values?

            ## TODO dedup
            ttt = torrent.find_one(file_name=self.file_name)
            print("file_name", self.file_name)
            print("saved thing is now", ttt)
            self.infohash = ttt["infohash"]
            self.seed_count = ttt["seed_count"]
            self.chk_fail_last = ttt["chk_fail_last"]
            self.chk_fail_count = ttt["chk_fail_count"]
            self.chk_success_last = ttt["chk_success_last"]
            self.chk_success_count = ttt["chk_success_count"]

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
    def newest():
        #last = torrent.find_one(order_by='-file_name')
        last = torrent.find_one(order_by='-id')
        if last == None:
            return 0
        else:
            return last["id"]

    @staticmethod
    def populate(count=1, col="r", only_count_absent=False):
        base = Tor.newest() + 1
        for n in range(0,count):
            newest = base + n
            print("[debug] populate :", n, base, newest)

            if Tor.is_known_missing(newest):
                print(".", newest)
                continue

            new_tor = Tor(newest)
            #if new_tor.exists_in_db:
            #    print(f"Found {new_tor.id} in db. Skipping")
            #    continue
            #
            #print(f"[debug] Did not find {new_tor.id} in db")
            #new_tor.get_from_file()
            #new_tor.save()


    def generate_libgen_torrent_filename(self):
        name = (self.id - 1 ) * 1000
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
        tracker_in_db = set([t["name"] for t in tracker.find()])
        tracker_new = tracker_in_torrent - tracker_in_db

        #print("tarcker in db: ",tracker_in_db)
        #print("tracker in torrent", set(tracker_in_torrent))
        #print("tracker new:",tracker_new)

        if len(tracker_new) == 0:
            return

        print(f"[+] Adding {len(tracker_new)} new tracker")
        for name in tracker_new:
            #print(f"[debug] insertring: {name}")
            tracker.insert(dict(name=name,
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
        tor = torrent.findone(id=["self.filename"])
        if tor == None: ## ugly!
            # create new
            pass # TODO
        else:
            print("ihihiihihihi", tor["infohash"])




    ##### TODO TODO TODO TODO 
    ##### TODO TODO TODO TODO 
    ##### TODO TODO TODO TODO 
    def save_to_db(self):
        print(f'[+] Saving torrent to DB from file {self.full_path} ')
        ti = lt.torrent_info(str(self.full_path))

        self.process_tracker(ti)

        infohash = str(ti.info_hashes().get_best())
        ##### TODO TODO TODO TODO 
        torrent.insert(dict(file_name=self.file_name,
                            id=self.id,
                            infohash = infohash,
                            chk_fail_count = 0,
                            chk_fail_last = None,
                            chk_success_count = 0,
                            chk_success_last = None,
                            ))

        #new_tracker = [e.url for e in ti.trackers()]
        #trackers.update_ignore()

        log.insert(dict(name=self.file_name,
                        status=f"added torrent {self.id}",
                        datetime=datetime.utcnow()))

    def is_known_missing( newest, col="r"):
        return newest *1000 in config["catalogue"]["r"]["known_missing"]


    def peer_exchange(self):
        from ttsfix import scraper
        all_tracker = Tracker.all()
        print(f"all tracker: {all_tracker}")

        scraper = scraper.Scraper(
            infohashes=[self.infohash,],
            #trackers=trackers,
            trackers=["udp//:tracker.opentrackr.org:1337"],
            )
        results = scraper.scrape()
        return results


    @staticmethod
    def peer_crawl( n=1):
        for n in range(0,n):
            oldest = torrent.find(order_by='chk_success_last').__next__() # maybe -chk..
            print(oldest["id"], oldest["infohash"])

            tor = Tor(oldest["id"])

            tor.peer_exchange()
            
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

class Tracker:
    def __init__(self):
        pass
    @staticmethod
    def all():
        print(tracker.find())

class Db:
    def __init__(self):
        if tracker.find_one() == None:
            print("[+] init.db.tracker")
            tracker.create_column('name', db.types.text)
            tracker.create_column('chk_success_count', db.types.integer)
            tracker.create_column('chk_fail_count', db.types.integer)
            tracker.create_column('chk_fail_last', db.types.datetime)
            tracker.create_column('chk_success_last', db.types.datetime)
            # tracker.create_index(["name"])
            # foo.create_column('foo', unique=True)

        if torrent.find_one() == None:
            print("[+] init.db.torrent")
            torrent.create_column('file_name', db.types.text)
            torrent.create_column('seed_count', db.types.integer)
            torrent.create_column('chk_fail_last', db.types.datetime)
            torrent.create_column('chk_fail_count', db.types.integer)
            torrent.create_column('chk_success_last', db.types.datetime)
            torrent.create_column('chk_success_count', db.types.integer)
            torrent.create_column('infohash', db.types.text)
            #torrent.create_column('', db.types.)
            # torrent.create_index(["file_name"])

        if log.find_one() == None:
            print("[+] init.db.log")
            log.create_column('name', db.types.text)
            log.create_column('status', db.types.text)
            log.create_column('datetime', db.types.datetime)

    def count_and_print(self, table):
        print(f"[i] table {table.name} has {table.count()} rows with columns:")
        print(f"    {table.columns}")


    def info(self):
        #for table in db.tables:
        for table in [tracker, torrent, log]:
            self.count_and_print(table)

    def integrety_chk(self):
        ### make sure no torrents are missingeg
        ### e.g. make sure that if we notice 0,1,2 and 4 but not 3

        # make sure ID and file_name fitt !
        pass



def load_config():
    return toml.load(CONFIG)

sqll = Db()
#sqll.integrety_chk()
#sqll.info()

config = load_config()
#print(config)

#Tor.integrety_check_libgen()
Tor.populate(count=160, only_count_absent=True)
#Tor.peer_crawl()


ttt = Tor(10)
print(ttt)
ttt.info()


