############
### main ###
############

scrape:
	poetry run python libgen_torrent_cardiography/mgmt.py scrape output
	# Merge main db file with wal
	sqlite3 data/ltc.sqlite  VACUUM;

populate:
	poetry run python libgen_torrent_cardiography/mgmt.py populate
	# Merge main db file with wal
	sqlite3 data/ltc.sqlite  VACUUM;

.PHONY: output
output:
	poetry run python libgen_torrent_cardiography/mgmt.py output

info:
	poetry run python libgen_torrent_cardiography/mgmt.py info

#################
### db things ###
#################

rm_mgmt_db:
	rm data/ltc.sqlite || true

restart: rm_mgmt_db populate

dbinfo:
	bash tools/dbinfo.sh

dbdump:
	bash tools/dbdump.sh


####################
### setup things ###
####################

env:
	poetry install

##################
### dev things ###
##################

dev_info:
	poetry run python examples/info.py

dev_lbt:
	poetry run python examples/lbt_info.py

dev_peers:
	poetry run python examples/fetch_peers.py

