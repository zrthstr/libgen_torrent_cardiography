import bencoding, hashlib

objTorrentFile = open("r_000.torrent", "rb")
decodedDict = bencoding.bdecode(objTorrentFile.read())

info_hash = hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest()
print(info_hash)
