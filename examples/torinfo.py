
import libtorrent as lt
import time
import sys

ses = lt.session()
ses.listen_on(6881, 6891)
params = {
    'save_path': '/tmp/torr',
    'storage_mode': lt.storage_mode_t(2),
    #'trackers"': 'udp//:9.rarbg.to:2740'
    'trackers': ['udp//:9.rarbg.to:2740','udp//:explodie.org:6969','udp//:opentor.org:2710'],
    }

#link = "magnet:?xt=urn:btih:4fabfdfe37295ee2cb1ac2440f45e36ce022b209"
link = "magnet:?xt=urn:btih:63a04291a8b266d968aa7ab8a276543fa63a9e84"

print(dir(lt))
h = lt.add_magnet_uri(ses, link, params)

print("hhhh:", dir(h))


#h.add_tracker([
#    "udp//:explodie.org:6969",
#    "udp//:9.rarbg.to:2740",
#    "udp//:opentor.org:2710"]) ## aparently this can directly into parms


print(dir(ses))

#print("DHP PEERS:",ses.dht_get_peers())

#ses.add_dht_router("router.utorrent.com", 6881)
#ses.add_dht_router("router.bittorrent.com", 6881)
#ses.add_dht_router("dht.transmissionbt.com", 6881)
#ses.start_dht()

while (not h.has_metadata()):
    time.sleep(1.1)
    pass

torinfo = h.get_torrent_info()

#print(dir(torinfo))
#print(torinfo.nodes())
#print(torinfo.web_seeds())

#print(torinfo.name())
#print(torinfo.creation_date())
#print(torinfo.info_hash())
#print(lt.make_magnet_uri(torinfo))

for tracker in torinfo.trackers():
    print(tracker)
    print(dir(tracker))
    print("msg:", tracker.message)
    print("next annon:", tracker.next_announce)
    print("next annon in:", tracker.next_announce_in())
    #print("next annon cann:", tracker.can_announce())
    print("is_working:", tracker.is_working())
