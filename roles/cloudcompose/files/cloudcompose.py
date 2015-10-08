#!/usr/bin/env python

import requests
import sh
import socket
import sys
import argparse

IP = socket.gethostbyname(socket.gethostname())
BASEURL = 'https://dl.dropboxusercontent.com/u/2096546/tmp/onapp/'
COMPOSEFILE = '/root/docker-compose.yml'
PROJECT = 'cloudnet'


def update_software():
    print 'Updating CloudCompose stack...'
    sh.apt_get('update')
    sh.apt_get('-y', 'install', 'docker')
    sh.pip('install', '-U', 'docker-compose')


def compose_init():
    compose_url = '{}/{}'.format(BASEURL, IP)
    get_compose_file = requests.get(compose_url)

    if get_compose_file.status_code == 200:
        with open(COMPOSEFILE, 'w') as f:
            f.write(get_compose_file.content)
        return sh.docker_compose('-p', PROJECT, '-f', COMPOSEFILE, 'up', '-d')
    else:
        print 'Unable to retrieve compose file...'
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--update', help="Update CloudCompose", action="store_true")
    parser.add_argument('--init', help="Initialize CloudCompose", action="store_true")
    parser.add_argument('--ps', help="List containers", action="store_true")
    parser.add_argument('--start', help="Start containers", action="store_true")
    parser.add_argument('--stop', help="Stop containers", action="store_true")
    parser.add_argument('--kill', help="Kill containers", action="store_true")
    parser.add_argument('--rm', help="Remove containers", action="store_true")

    args = parser.parse_args()
    if args.init:
        print compose_init()
    elif args.update:
        update_software()
    elif args.ps:
        print sh.docker_compose('-p', PROJECT, '-f', COMPOSEFILE, 'ps')
    elif args.start:
        print sh.docker_compose('-p', PROJECT, '-f', COMPOSEFILE, 'start')
    elif args.stop:
        print sh.docker_compose('-p', PROJECT, '-f', COMPOSEFILE, 'stop')
    elif args.kill:
        print sh.docker_compose('-p', PROJECT, '-f', COMPOSEFILE, 'kill')
    elif args.rm:
        print 'To remove the containers, please run:\ndocker-compose -p {} -f {} rm'.format(PROJECT, COMPOSEFILE)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
