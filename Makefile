
info:
	poetry run python examples/info.py

lbt:
	poetry run python examples/lbt_info.py

peers:
	#poetry run python examples/fetch_peers.py
	poetry run python examples/fetch_peers.py

# https://gist.github.com/francoism90/4db9efa5af546d831ca47208e58f3364
ret:
	poetry run python retrieve.py 'magnet:?xt=urn:btih:9FC20B9E98EA98B4A35E6223041A5EF94EA27809&dn=%5Bmonova.org%5D+ubuntu-20.04-desktop-amd64.iso&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969'

mgmt:
	poetry run python libgen_torrent_cardiography/mgmt.py

rm_mgmt_db:
	rm data/ltc.sqlite

restart: rm_mgmt_db mgmt

dbinfo:
	bash tools/dbinfo.sh

dbdump:
	bash tools/dbdump.sh
