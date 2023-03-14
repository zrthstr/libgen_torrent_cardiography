#!/usr/bin/env bash

DBFILE="data/ltc.sqlite"
#sqlite3 $DBFILE 'select * from tracker;'
sqlite3 $DBFILE 'select * from torrent'
#sqlite3 $DBFILE 'select * from log'

#sqlite3 $DBFILE 'select count(*) from tracker;'
sqlite3 $DBFILE 'select count(*) from torrent'
sqlite3 $DBFILE 'select count(*) from log'
