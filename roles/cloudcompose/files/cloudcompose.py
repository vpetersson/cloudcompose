#!/usr/bin/env python

import requests
import sh
import socket
import sys
import argparse
import syslog
import ConfigParser
import time
import datetime

config = ConfigParser.RawConfigParser()
config.read('/usr/local/etc/cloudcompose.cfg')
IP = socket.gethostbyname(socket.gethostname())
BASEURL = config.get('main', 'base_url')
COMPOSEFILE = config.get('main', 'compose_file')
PROJECT = config.get('main', 'project')
RETRY_PERIOD = config.get('main', 'retry_period')

def logger(msg, error=False):
    print(msg)
    if not error:
        syslog.syslog(msg)
    else:
        syslog.syslog(syslog.LOG_ERR, msg)


def update_software():
    logger('Updating CloudCompose stack...')
    sh.apt_get('update')
    sh.apt_get('-y', 'install', 'docker')
    sh.pip('install', '-U', 'docker-compose')


def compose_init():
    logger('Initializing CloudCompose...')
    compose_url = None
    compose_url_ip = '{}/{}'.format(BASEURL, IP)
    compose_url_fallback = '{}/{}'.format(BASEURL, 'docker-compose.yml')
    give_up_at = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=int(RETRY_PERIOD))

    # Keep retrying during RETRY_PERIOD.
    while give_up_at > datetime.datetime.utcnow():
        if requests.head(compose_url_ip).status_code == 200:
            compose_url = compose_url_ip
            break
        else:
            logger(
                'Unable to fetch IP specific compose file. Giving in {}.)'
                .format(give_up_at - datetime.datetime.utcnow()))
            time.sleep(10)

    if not compose_url:
        if requests.head(compose_url_fallback).status_code == 200:
            logger('Unable to fetch IP specific file. Using fallback-file.')
            compose_url = compose_url_fallback
        else:
            logger('Unable to retrieve compose file...', error=True)
            sys.exit(1)

    get_compose_file = requests.get(compose_url)

    if get_compose_file.status_code == 200:
        logger('Successfully fetched compose file from {}...'
               .format(compose_url))
        with open(COMPOSEFILE, 'w') as f:
            f.write(get_compose_file.content)
        try:
            compose = sh.docker_compose(
                '-p', PROJECT, '-f', COMPOSEFILE, 'up', '-d'
            )
            logger(
                'Compose exited with exit code {}'.format(compose.exit_code)
            )
            return compose
        except:
            logger('Unable to launch Docker Compose.')
    else:
        logger('Unable to retrieve compose file...', error=True)
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
