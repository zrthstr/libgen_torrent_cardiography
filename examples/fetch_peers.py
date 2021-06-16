

import libtorrent as lt
from ttsfix import scraper
#from torrent_tracker_scraper import scraper

def infohash_and_tracker_from_file(filename):
    print("ff", filename)
    ti = lt.torrent_info(filename)
    print(f"Info hash of {filename} is: ",ti.info_hash())
    info_hash = ti.info_hash()
    trackers = ti.trackers()

    trackers = [l.url for l in list(trackers)]

    return info_hash, trackers



def get_swarm_info(info_hash, trackers):
    from ttsfix import scraper
    scraper = scraper.Scraper(
            infohashes=[info_hash,],
            #trackers=trackers,
            trackers=["udp//:tracker.opentrackr.org:1337"],
            )
    results = scraper.scrape()
    return results


def parse_peer_result(result):
    for r in result:
        print(r)


def process_torrents(tf):
    print("tf:",tf)

    info_hash, tracker = infohash_and_tracker_from_file(tf)

    # tracker = clense(tracker, bad_tracker)

    print("Infohash:", info_hash.to_bytes().hex())
    print(f"Trackers: {tracker[0]} and {len(tracker)} more")

    info_hash = info_hash.to_bytes().hex()

    results = get_swarm_info(info_hash, tracker)
    print(results)

    parse_peer_result(results)



process_torrents("r_000.torrent")
