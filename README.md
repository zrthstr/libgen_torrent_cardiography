# Monitor Library Genesis' and Sci-Hub's torrent health
This GitHub [repository](https://github.com/zrthstr/libgen_torrent_cardiography/) generates https://zrthstr.github.io/libgen_torrent_cardiography/index.html and [torrent.json](https://zrthstr.github.io/libgen_torrent_cardiography/torrent.json) with the help of GitHub Actions, tracking the number of seeders per torrent.

This project is inspired by https://phillm.net/libgen-stats-table-raw.php and also borrows some of its html,
and is ment to be used via https://github.com/subdavis/libgen-seedtools.

## About LG data and torrents
* stats http://libgen.lc/stat.php
* libgen consists of a few different catalogues of files
there appear to be:
  books, standards, comics, fiction, magazines, scimag, fiction_rus

### scimag aka "sci-hub"
* http://libgen.gs/scimag/index.php?s=test
* also currently https://sci-hub.do/
* source http://gen.lib.rus.ec/scimag/repository_torrent/
* 100k files per torrent
* more than 85,483,812 papers
* example sm_00000000-00099999.torrent

### fiction aka "f"
* 1000 files per torrent
* source http://libgen.rs/fiction/repository_torrent/
* aprox 2.6m files/books
* f_0 - f_2327000.torrent

### books aka "r" 
* 1000 files per torrent
* source http://libgen.rs/repository_torrent/
* aprox 3m files/books
* t_000.torrent - r_2999000.torrent

### magazines (external)
* 580290 files
* 13.496 terabytes
* apparently, see http://magzdb.org/

### fiction_rus
* ???


### there are a few ways to find seeders/peers
only `tracker/infowire` is currently implemented and running
* DHT/PEX
* from trackers
  * TCP/HTTP
  * UDP/Infowire [BEP14](https://www.bittorrent.org/beps/bep_0015.html)
* LSD - Local Service Discovery (BEP14)

### rand info
* https://libgen.life/ Some community forum
* https://news.ycombinator.com/item?id=21692222
* UDP NAT PUNCH https://github.com/inconshreveable/ngrok/issues/26#issuecomment-69535251
* https://en.wikipedia.org/wiki/Kademlia
* https://en.wikipedia.org/wiki/Internet_Gateway_Device_Protocol
* http://www.bittorrent.org/beps/bep_0033.html
