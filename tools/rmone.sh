#!/usr/bin/bash

sqlite3 data/ltc.sqlite 'select * from torrent where id = 10'
sqlite3 data/ltc.sqlite 'DELETE from torrent where id = 10'
sqlite3 data/ltc.sqlite 'select * from torrent where id = 10'
