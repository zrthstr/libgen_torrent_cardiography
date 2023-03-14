#!/usr/bin/env python3
import libtorrent as lt
import time
import json
import os

def write_json(path, contents):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(contents, f, default=str, indent=4, sort_keys=True)

def add_torrent(ses, filename, options):
    atp = lt.add_torrent_params()

    if filename.startswith('magnet:'):
        atp = lt.parse_magnet_uri(filename)

    atp.save_path = options.save_path
    atp.storage_mode = lt.storage_mode_t.storage_mode_sparse
    atp.flags |= lt.torrent_flags.duplicate_is_error \
        | lt.torrent_flags.auto_managed \
        | lt.torrent_flags.duplicate_is_error \
        | lt.torrent_flags.upload_mode

    ses.async_add_torrent(atp)

def get_torrent_info(info):
    attributes = [
        'name',
        'comment',
        'creator',
        'total_size',
        'piece_length',
        'num_pieces',
        'info_hash',
        'num_files',
        'priv',
        'creation_date',
    ]

    entry = {}

    for attribute in attributes:
        entry[attribute] = getattr(info, attribute, None)()

    return entry

def get_file_info(file):
    attributes = [
        'path',
        'symlink_path',
        'offset',
        'size',
        'mtime',
        'filehash',
        'pad_file',
        'hidden_attribute',
        'executable_attribute',
        'symlink_attribute',
    ]

    entry = {}

    for attribute in attributes:
        entry[attribute] = getattr(file, attribute, None)

    return entry

def main():
    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('-p', '--port', type='int', help='set listening port')

    parser.add_option(
        '-i', '--listen-interface', type='string',
        help='set interface for incoming connections', )

    parser.add_option(
        '-o', '--outgoing-interface', type='string',
        help='set interface for outgoing connections')

    parser.add_option(
        '-d', '--max-download-rate', type='float',
        help='the maximum download rate given in kB/s. 0 means infinite.')

    parser.add_option(
        '-u', '--max-upload-rate', type='float',
        help='the maximum upload rate given in kB/s. 0 means infinite.')

    parser.add_option(
        '-c', '--connections_limit', type='int',
        help='the global limit on the number of connections opened.')

    parser.add_option(
        '-s', '--save-path', type='string',
        help='the path where the downloaded file/folder should be placed.')

    parser.add_option(
        '-r', '--proxy-host', type='string',
        help='sets HTTP proxy host and port (separated by \':\')')

    parser.add_option(
        '-t', '--timeout', type='int',
        help='the number of seconds to wait to receive any data from the torrents.')

    parser.set_defaults(
        port=6881,
        listen_interface='0.0.0.0',
        outgoing_interface='',
        max_download_rate=0,
        max_upload_rate=0,
        connections_limit=400,
        save_path='.',
        proxy_host='',
        timeout=90
    )

    (options, args) = parser.parse_args()

    if options.port < 0 or options.port > 65525:
        options.port = 6881

    options.max_upload_rate *= 1000
    options.max_download_rate *= 1000

    if options.max_upload_rate <= 0:
        options.max_upload_rate = -1
    if options.max_download_rate <= 0:
        options.max_download_rate = -1

    settings = {
        'user_agent': 'libtorrent/' + lt.__version__,
        'listen_interfaces': '%s:%d' % (options.listen_interface, options.port),
        'download_rate_limit': int(options.max_download_rate),
        'upload_rate_limit': int(options.max_upload_rate),
        'connections_limit': int(options.connections_limit),
        'dht_bootstrap_nodes': 'router.bittorrent.com:6881,dht.transmissionbt.com:6881,router.utorrent.com:6881,',
        'alert_mask': lt.alert.category_t.all_categories,
        'outgoing_interfaces': options.outgoing_interface,
        'announce_to_all_tiers': True,
        'announce_to_all_trackers': True,
        'auto_manage_interval': 5,
        'auto_scrape_interval': 0,
        'auto_scrape_min_interval': 0,
        'max_failcount': 1,
        'aio_threads': 8,
        'checking_mem_usage': 2048,
    }

    if options.proxy_host != '':
        settings['proxy_hostname'] = options.proxy_host.split(':')[0]
        settings['proxy_type'] = lt.proxy_type_t.http
        settings['proxy_port'] = options.proxy_host.split(':')[1]

    ses = lt.session(settings)

    # map torrent_handle to torrent_status
    torrents = {}
    alerts_log = []
    process_time = time.time() + int(options.timeout)

    for f in args:
        print('Adding %s' % (f))
        add_torrent(ses, f, options)

    # process torrents data
    while time.time() < process_time:
        alerts = ses.pop_alerts()
        for a in alerts:
            alerts_log.append(a.message())

            # add new torrents to our list of torrent_status
            if isinstance(a, lt.add_torrent_alert):
                h = a.handle
                h.set_max_connections(60)
                h.set_max_uploads(-1)
                torrents[h] = h.status()

            # update our torrent_status array for torrents that have
            # changed some of their state
            if isinstance(a, lt.state_update_alert):
                for s in a.status:
                    torrents[s.handle] = s

        if len(alerts_log) > 20:
            alerts_log = alerts_log[-20:]

        time.sleep(0.5)

        ses.post_torrent_updates()

    # parse torrents
    ses.pause()

    for h, t in torrents.items():
        print('Parsing %s' % (t.info_hash))

        if not h.is_valid() or not t.has_metadata:
            print('Failed to parse %s' % (t.info_hash))
            continue

        # create path
        path = [options.save_path, str(t.info_hash)]
        os.makedirs(os.path.join(*path), exist_ok=True)

        # write info
        info = t.handle.get_torrent_info()

        write_json(os.path.join(*path, 'info.json'), get_torrent_info(info))

        # write files
        files = []
        for index, file in enumerate(info.files()):
            files.append(get_file_info(file))

        write_json(os.path.join(*path, 'files.json'), files)

        # write trackers
        write_json(os.path.join(*path, 'trackers.json'), t.handle.trackers())

        # unsubscribe from torrent
        print('Unsubscribing from %s' % (t.info_hash))

        ses.remove_torrent(h)

main()
