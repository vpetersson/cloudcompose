#!/usr/bin/env python

import requests
import sh
import socket
import sys
import argparse
import syslog
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('/usr/local/etc/cloudcompose.cfg')
IP = socket.gethostbyname(socket.gethostname())
BASEURL = config.get('main', 'base_url')
COMPOSEFILE = config.get('main', 'compose_file')
PROJECT = config.get('main', 'project')


def update_software():
    print 'Updating CloudCompose stack...'
    syslog.syslog('Updating CloudCompose stack...')
    sh.apt_get('update')
    sh.apt_get('-y', 'install', 'docker')
    sh.pip('install', '-U', 'docker-compose')


def compose_init():
    syslog.syslog('Initializing CloudCompose...')
    compose_url = None
    compose_url_ip = '{}/{}'.format(BASEURL, IP)
    compose_url_fallback = '{}/{}'.format(BASEURL, 'docker-compose.yml')

    if requests.head(compose_url_ip).status_code == 200:
        compose_url = compose_url_ip
    elif requests.head(compose_url_fallback).status_code == 200:
        compose_url = compose_url_fallback
    else:
        print 'Unable to retrieve compose file...'
        syslog.syslog(syslog.LOG_ERR, 'Unable to retrieve compose file...')
        sys.exit(1)

    get_compose_file = requests.get(compose_url)

    if get_compose_file.status_code == 200:
        syslog.syslog(
            'Successfully fetched compose file from {}...'.format(compose_url)
        )
        with open(COMPOSEFILE, 'w') as f:
            f.write(get_compose_file.content)
        try:
            compose = sh.docker_compose(
                '-p', PROJECT, '-f', COMPOSEFILE, 'up', '-d'
            )
            syslog.syslog(
                'Compose exited with exit code {}'.format(compose.exit_code)
            )
            return compose
        except:
            syslog.syslog('Unable to launch Docker Compose.')
    else:
        print 'Unable to retrieve compose file...'
        syslog.syslog(syslog.LOG_ERR, 'Unable to retrieve compose file...')
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--update', help="Update CloudCompose", action="store_true"
    )
    parser.add_argument(
        '--init', help="Initialize CloudCompose", action="store_true"
    )
    parser.add_argument(
        '--ps', help="List containers", action="store_true"
    )
    parser.add_argument(
        '--start', help="Start containers", action="store_true"
    )
    parser.add_argument(
        '--stop', help="Stop containers", action="store_true"
    )
    parser.add_argument(
        '--kill', help="Kill containers", action="store_true"
    )
    parser.add_argument(
        '--rm', help="Remove containers", action="store_true"
    )

    args = parser.parse_args()
    if args.init:
        compose_init()
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
        print """
        To remove the containers, please run:\ndocker-compose -p {} -f {} rm
        """.format(PROJECT, COMPOSEFILE)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
