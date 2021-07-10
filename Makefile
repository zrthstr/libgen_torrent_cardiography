############
### main ###
############

mgmt:
	poetry run python libgen_torrent_cardiography/mgmt.py
	# Merge main db file with wal
	sqlite3 data/ltc.sqlite  VACUUM;

.PHONY: output
output:
	poetry run python libgen_torrent_cardiography/mgmt.py output

#################
### db things ###
#################

rm_mgmt_db:
	rm data/ltc.sqlite || true

restart: rm_mgmt_db mgmt

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

info:
	poetry run python examples/info.py

lbt:
	poetry run python examples/lbt_info.py

peers:
	poetry run python examples/fetch_peers.py

