############
### main ###
############

mgmt:
	poetry run python libgen_torrent_cardiography/mgmt.py

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


##################
### dev things ###
##################

info:
	poetry run python examples/info.py

lbt:
	poetry run python examples/lbt_info.py

peers:
	poetry run python examples/fetch_peers.py

