
import dataset

class Database:

    def __init__(self):
        self.db = self.connect()
        self.tracker = self.db['tracker']
        self.torrent = self.db['torrent']
        self.log = self.db['log']

        self.chk_schema()


    def connect(self):
        # TODO, get this value from config file
        return dataset.connect('sqlite:///data/ltc.sqlite')

    def chk_schema(self):
        if self.tracker.find_one() == None:
            print("[+] init.db.tracker")
            self.tracker.create_column('name', self.db.types.text)
            self.tracker.create_column('chk_success_count', self.db.types.integer)
            self.tracker.create_column('chk_fail_count', self.db.types.integer)
            self.tracker.create_column('chk_fail_last', self.db.types.datetime)
            self.tracker.create_column('chk_success_last', self.db.types.datetime)
            # tracker.create_index(["name"])
            # foo.create_column('foo', unique=True)

        if self.torrent.find_one() == None:
            print("[+] init.db.torrent")
            self.torrent.create_column('file_name', self.db.types.text)
            self.torrent.create_column('seed_count', self.db.types.integer)
            self.torrent.create_column('leech_count', self.db.types.integer)
            self.torrent.create_column('chk_fail_last', self.db.types.datetime)
            self.torrent.create_column('chk_fail_count', self.db.types.integer)
            self.torrent.create_column('chk_success_last', self.db.types.datetime)
            self.torrent.create_column('chk_success_count', self.db.types.integer)
            self.torrent.create_column('infohash', self.db.types.text)
            #self.torrent.create_column('', self.db.types.)
            # self.torrent.create_index(["file_name"])

        if self.log.find_one() == None:
            print("[+] init.db.log")
            self.log.create_column('name', self.db.types.text)
            self.log.create_column('status', self.db.types.text)
            self.log.create_column('datetime', self.db.types.datetime)


    def count_and_print(self, table):
        print(f"[i] table {table.name} has {table.count()} rows with columns:")
        print(f"    {table.columns}")


    def info(self):
        #for table in db.tables:
        for table in [self.tracker, self.torrent, self.log]:
            self.count_and_print(table)

    def integrety_chk(self):
        print("this __SHOULD__ be and integrety check")
        ### make sure:
        ### * no torrents are missingeg
        ###     e.g. make sure that if we notice 0,1,2 and 4 but not 3
        ### * ID and file_name fitt
        ### * no infohash are double
        pass


