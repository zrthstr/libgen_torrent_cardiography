# Monitor Library Genesis and Sci-Hub' torrent health
Track the number of seeders per torrent using various sources

## About LG data and torrents
* stats http://libgen.lc/stat.php
* libgen consists of a few different catalogues of files
there appear to be:
  standards, comics, fiction, magazines, scimag, fiction_rus

### scimag aka "sci-hub"
* http://libgen.gs/scimag/index.php?s=test
* also currently https://sci-hub.do/
* 100k files in torrent
* more than 85,483,812 papers
* src and example: http://gen.lib.rus.ec/scimag/repository_torrent/sm_00000000-00099999.torrent

### f aka "fiction"
* 1000 files are on torrent
* see http://libgen.rs/fiction/repository_torrent/
* f -> fiction
* f_0 - f_2327000.torrent

### r aka "books"
* http://libgen.rs/repository_torrent/
* r -> ???????
* t_000.torrent - r_2999000.torrent

### magazines (external)
* 580 290 files
* 13.496 terabytes
* apparently, see http://magzdb.org/

### fiction_rus
* ???



### there are a few ways to find seeder/peers
* DHT/PEX
* from trackers
  * TCP/HTTP
  * UDP/Infowire [BEP14](https://www.bittorrent.org/beps/bep_0015.html)
* LSD - Local Service Discovery (BEP14)

### rand info
* https://libgen.life/ Some comunity forum
* https://news.ycombinator.com/item?id=21692222
* UDP NAT PUNCH https://github.com/inconshreveable/ngrok/issues/26#issuecomment-69535251
* https://en.wikipedia.org/wiki/Kademlia
* https://en.wikipedia.org/wiki/Internet_Gateway_Device_Protocol
* http://www.bittorrent.org/beps/bep_0033.html
