
# https://stackoverflow.com/questions/46025771/python3-calculating-torrent-hash
#
# see https://pypi.org/project/tracker-scraper/   https://pypi.org/project/tracker-scraper/
# https://pypi.org/project/tracker-scraper/

import os
import requests
#import bencode
#from torrentool.api import Torrent

import bs4

TORRENT_SRC = "https://libgen.is/repository_torrent/"
TORRENT_DIR = "data/torrent"
TORRENT_DB = "data/torrent.toml"


def inspect(url):
    response = requests.get(TORRENT_SRC + "/" + url)
    print(response.text)
    print(bencode.decode(response.text))


def find_all_torrents_on_libgen():
    torrents = set()

    response = requests.get(TORRENT_SRC)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    links = soup.select('a')

    for link in links:
        name = link.get_text()
        if name.endswith(".torrent"):
            torrents.add(name)
    return torrents


def find_all_local_torrents_dir():
    # for now lets use a dir..
    torrents = set()
    for d in os.listdir(TORRENT_DIR):
        if d.endswith(".torrent") and d.startswith("r_"):
            torrents.add(d)
    return torrents


def find_all_local_torrents_toml():
    with open(TORRENT_DB, 'rb') as fin:
        torrents = toml.load(fin)


def save_all_torrents_to_toml():
    with open(TORRENT_DB, 'w') as f:
        toml.dump(torrents, f, encoder=None)


def bulk_fetch():
    pass

def update():
    pass


def integrity_info_dir(torrents_remote, torrents_local):
    torrents_local_count = len(torrents_local)
    torrents_remote_count = len(torrents_remote)
    missing_torrent_count = torrents_remote_count - torrents_local_count

    print(f"We have {torrents_local_count} torrents.")
    print(f"There are {torrents_remote_count} torrents on libgen.")
    print(f"We therefor expect to miss {missing_torrent_count} torrents")

    if missing_torrent_count < 0:
        raise("somthing is not quite right")
    if missing_torrent_count == 0:
        print("All torrents present")

    torrents_missing = torrents_remote - torrents_local
    print("torrents_missing:", len(torrents_missing))


def integrity_info_toml(torrents_remote, torrents_local, torrents_toml)
    torrents_local_count = len(torrents_local)
    torrents_remote_count = len(torrents_remote)
    torrents_toml_count = len(torrents_toml)

    missing_torrent_toml_count = torrents_remote_count - torrents_toml_count
    missing_torrent_local_count = torrents_remote_count - torrents_local_count

    print(f"We have {torrents_local_count} torrents in dir.")
    print(f"We have {torrents_toml_count} torrents in toml.")
    print(f"There are {torrents_remote_count} torrents on libgen.")

    print(f"We therefor expect to miss {missing_torrent_toml_count} torrents in toml")
    print(f"We therefor expect to miss {missing_torrent_local_count} torrents in dir")

    if missing_torrent_toml_count < 0:
        raise("somthing is not quite right (toml)")
    if missing_torrent_local_count < 0:
        raise("somthing is not quite right (dir)")
    if missing_torrent_toml_count == missing_torrent_local_count == 0:
        print("All torrents present")

    #torrents_missing = torrents_remote - torrents_local
    #print("torrents_missing:", len(torrents_missing))


def fetch_torrent(torrent):
    url = TORRENT_SRC + torrent
    torrent_dest = TORRENT_DIR + "/" + torrent
    r = requests.get(url)
    with open(torrent_dest, 'wb') as torrent_out:
        torrent_out.write(r.content)
    print("file fetched and writen")


def integrity_check_and_fetch_dir():
    # find out what torrents exist on lg
    # then find out what torrents exist locally
    # then fetch the diffrence
    torrents_remote = find_all_torrents_on_libgen()
    torrents_local = find_all_local_torrents_dir()
    integrity_info(torrents_remote, torrents_local)

    torrents_missing = torrents_remote - torrents_local
    for tm in torrents_missing:
        fetch_torrent(tm)

def integrity_check_and_fetch_toml()
    # find out what torrents exist on lg
    # find out what torrents exist in toml
    # get the difference
    # fetch the difference by
    #   first looking in local dir
    #   else fetching form server
    # add to dir and to toml
    # save toml
    torrents_remote = find_all_torrents_on_libgen()
    torrents_local_dir = find_all_local_torrents_dir()
    torrents_local_toml = find_all_local_torrents_toml()

#integrity_check_and_fetch_dir()
integrity_check_and_fetch_toml()






