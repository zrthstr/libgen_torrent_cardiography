import json
import dataset

# from jinja2 import Template
from jinja2 import Environment, FileSystemLoader, Template
from datetime import datetime


"""
output should look https://phillm.net/libgen-stats-formatted.php

[
  {
    "name": "2127000",
    "link": "http://gen.lib.rus.ec/repository_torrent/r_2127000.torrent",
    "created_unix": 1509322887,
    "size_bytes": 44290249082,
    "type": "books",
    "infohash": "330eaf4e90c19c38f646dc9aba3542c2f6f3d74f",
    "seeders": 4,
    "leechers": 2,
    "completed": 12,
    "scraped_date": 1624533399,
    "dht_peers": 15,
    "dht_scraped": 1624533399
  },
  {..}, ...
  ]

"""


class Output:
    def __init__(self, torrent_collection):
        self.torrent_collection = torrent_collection
        self.config = torrent_collection.config
        self.OUT_HTML = self.config["output"]["html"]
        self.OUT_JSON = self.config["output"]["json"]

    def kneed_data(self):
        out = []
        for torrent in self.torrent_collection.members:
            out.append(
                dict(
                    name=torrent.file_name,
                    link=torrent.url,
                    created_unix=torrent.creation_date,
                    size_bytes=torrent.size_bytes,
                    type=torrent.collection,
                    infohash=torrent.infohash,
                    seeders=torrent.seeders,
                    leechers=torrent.leechers,
                    completed=torrent.completed,
                    scraped_date=self.ts_from_dt_or_none(torrent.scrape_success_last),
                    # last_updated   = self.ts_from_dt_or_none(torrent.scrape_success_last),
                    last_updated=str(torrent.scrape_success_last),
                    dht_peers=torrent.dht_peers,
                    dht_scraped=torrent.dht_success_last,
                )
            )
        return out

    def ts_from_dt_or_none(self, dt):
        if dt:
            return int(datetime.timestamp(dt))
        return "n/a"

    def generate_json(self, data):
        for d in data:
            del d["last_updated"]

        json_out = json.dumps(data)

        with open(self.OUT_JSON, "w") as fd:
            fd.write(json_out)

    # def generate_html(self, extened=False, collections="all", max_seed=3):
    def generate_html(self, data):
        file_loader = FileSystemLoader("templates")
        env = Environment(loader=file_loader)
        template = env.get_template("torrent.html")

        output = template.render(data=data, update_time=datetime.utcnow())

        # print(output)
        with open(self.OUT_HTML, "w") as fd:
            fd.write(output)

    # def generate(self, extended=False):
    def generate(self):
        data = self.kneed_data()
        self.generate_html(data)
        self.generate_json(data)
