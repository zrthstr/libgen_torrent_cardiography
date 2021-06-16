#import toml
import dataset
#import requests
#import libtorrent as lt
#from pathlib import Path
from datetime import datetime



class Db:
    def __init__(self, db):
        self.tracker = db['tracker']
        self.torrent = db['torrent']
        self.log = db['log']

        if self.tracker.find_one() == None:
            print("[+] init.db.tracker")
            self.tracker.create_column('name', db.types.text)
            self.tracker.create_column('chk_success_count', db.types.integer)
            self.tracker.create_column('chk_fail_count', db.types.integer)
            self.tracker.create_column('chk_fail_last', db.types.datetime)
            self.tracker.create_column('chk_success_last', db.types.datetime)
            # tracker.create_index(["name"])
            # foo.create_column('foo', unique=True)

        if self.torrent.find_one() == None:
            print("[+] init.db.torrent")
            self.torrent.create_column('file_name', db.types.text)
            self.torrent.create_column('seed_count', db.types.integer)
            self.torrent.create_column('chk_fail_last', db.types.datetime)
            self.torrent.create_column('chk_fail_count', db.types.integer)
            self.torrent.create_column('chk_success_last', db.types.datetime)
            self.torrent.create_column('chk_success_count', db.types.integer)
            self.torrent.create_column('infohash', db.types.text)
            #self.torrent.create_column('', db.types.)
            # self.torrent.create_index(["file_name"])

        if self.log.find_one() == None:
            print("[+] init.db.log")
            self.log.create_column('name', db.types.text)
            self.log.create_column('status', db.types.text)
            self.log.create_column('datetime', db.types.datetime)

    def count_and_print(self, table):
        print(f"[i] table {table.name} has {table.count()} rows with columns:")
        print(f"    {table.columns}")


    def info(self):
        #for table in db.tables:
        for table in [self.tracker, self.torrent, self.log]:
            self.count_and_print(table)

    def integrety_chk(self):
        ### make sure:
        ### * no torrents are missingeg
        ###     e.g. make sure that if we notice 0,1,2 and 4 but not 3
        ### * ID and file_name fitt
        ### * no infohash are double
        pass


