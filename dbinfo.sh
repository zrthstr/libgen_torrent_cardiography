#!/usr/bin/env bash

DBFILE="data/ltc.sqlite"
sqlite3 $DBFILE 'select * from tracker limit 5;'
sqlite3 $DBFILE 'select * from torrent limit 5'
sqlite3 $DBFILE 'select * from log limit 5'


sqlite3 $DBFILE 'select count(*) from tracker;'
sqlite3 $DBFILE 'select count(*) from torrent'
sqlite3 $DBFILE 'select count(*) from log'





sqlite3 $DBFILE 'select * from torrent '
sqlite3 $DBFILE 'select * from torrent where id = 10'
