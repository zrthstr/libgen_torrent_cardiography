import dataset


class Database:
    def __init__(self, config):
        self.config = config
        self.db = self.connect()
        self.tracker = self.db["tracker"]
        self.torrent = self.db.create_table(
            "torrent",
            primary_id="infohash",
            primary_type=self.db.types.string(40),
        )
        self.log = self.db["log"]
        self.chk_schema()

    def connect(self):
        return dataset.connect(self.config["db"]["connection"])

    def chk_schema(self):
        if self.tracker.find_one() is None:
            print("[+] init.db.tracker")
            self.tracker.create_column("url", self.db.types.text)
            self.tracker.create_column("chk_success_count", self.db.types.integer)
            self.tracker.create_column("chk_fail_count", self.db.types.integer)
            self.tracker.create_column("chk_fail_last", self.db.types.datetime)
            self.tracker.create_column("chk_success_last", self.db.types.datetime)
            # tracker.create_index(["name"])
            # foo.create_column('foo', unique=True)

        ### NOTE
        ### ID is not uniq
        ### infohash is uniq!
        ###
        ### id is only uniq per collection
        ### id referes to the libgen id, not "a db id"

        if self.torrent.find_one() is None:
            print("[+] init.db.torrent")
            self.torrent.create_column("file_name", self.db.types.text)
            self.torrent.create_column("collection", self.db.types.text)
            self.torrent.create_column("seeders", self.db.types.integer)
            self.torrent.create_column("leechers", self.db.types.integer)
            self.torrent.create_column("completed", self.db.types.integer)
            self.torrent.create_column("dht_peers", self.db.types.integer)
            self.torrent.create_column("size_bytes", self.db.types.integer)
            self.torrent.create_column("creation_date", self.db.types.integer)
            self.torrent.create_column("scrape_fail_last", self.db.types.datetime)
            self.torrent.create_column("scrape_fail_count", self.db.types.integer)
            self.torrent.create_column("scrape_success_last", self.db.types.datetime)
            self.torrent.create_column("scrape_success_count", self.db.types.integer)
            self.torrent.create_column("dht_fail_last", self.db.types.datetime)
            self.torrent.create_column("dht_fail_count", self.db.types.integer)
            self.torrent.create_column("dht_success_last", self.db.types.datetime)
            self.torrent.create_column("dht_success_count", self.db.types.integer)

        if self.log.find_one() is None:
            print("[+] init.db.log")
            self.log.create_column("name", self.db.types.text)
            self.log.create_column("status", self.db.types.text)
            self.log.create_column("datetime", self.db.types.datetime)

    def count_and_print(self, table):
        print(f"[i] table {table.name} has {table.count()} rows with columns:")
        print(f"    {table.columns}")

    def info(self):
        # for table in db.tables:
        for table in [self.tracker, self.torrent, self.log]:
            self.count_and_print(table)

    def integrety_chk(self):
        ### make sure:
        ### * no torrents have been skipped
        ### * ID and file_name fitt
        pass
