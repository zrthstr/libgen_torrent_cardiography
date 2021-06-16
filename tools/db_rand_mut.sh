#!/usr/bin/env bash

DBFILE="data/ltc.sqlite"

sqlite3 $DBFILE 'select count(*) from torrent'

#sqlite3 $DBFILE 'select * from torrent limit 5'

#sqlite3 $DBFILE 'select * from torrent '

sqlite3 $DBFILE 'select * from torrent where id = 11'
sqlite3 $DBFILE 'UPDATE torrent set infohash = "1001010" where id = 11'
sqlite3 $DBFILE 'select * from torrent where id = 11'




sqlite3 $DBFILE 'select count(*) from torrent'
