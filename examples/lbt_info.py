

## https://www.programmersought.com/article/90372172615/


# python-libtorrent-bin
import libtorrent as lt

tf = "r_8000.torrent"
tf = "data/torrent/" + tf
ti = lt.torrent_info(tf)

print(ti)
print(dir(ti))


#print(ti.total_size())

print(ti.creation_date())
exit()


for attr, value in vars(ti).items():
    print("sss")
    print(attr, value)


print("ddd")

for f in ti.files():
    #print(dir(f))
    print(f.path)
    print(f.size)
    break

for f in ti.trackers():
    #print(dir(f))
    #print(type(f))
    print(f.url)
    #exit()
    #break


print("total size:",ti.total_size())

print("name:", ti.name())
print("is_valid:", ti.is_valid())
#print("orig_files: ", dir(ti.orig_files().file_path))
print("comment: ", ti.comment())
print("merkle_tree", ti.merkle_tree())
print("metadata (first 30 byte)", ti.metadata()[:30])


def metadata():

    print("metatdat benDecoded")
    import bencodepy
    md = bencodepy.decode( ti.metadata())
    #print(bencodepy.decode( ti.metadata()))
    #print(type(bencodepy.decode( ti.metadata())))

    for k, v in md.items():
        print(k, type(v))

    print(md[b"files"][0])

    print("len(files):", len(md[b"files"]))

    for k,v in md[b"files"][0].items():
        print(k,v)

    print("name:", md[b"name"])
    print("pieces (first 30 bytes):", md[b"pieces"][:30])
    print("piece length:",md[b"piece length"])

metadata()

#for f in ti.total_size():
#    print(dir.total_size())
#    break


print("Infohash:",str(ti.info_hash()))
print(type(str(ti.info_hash())))

#print(dir(ti.info_hashes().get))

