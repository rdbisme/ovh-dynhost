#!/usr/bin/env python
"""
This scripts updates the DynHost configured on your domain registered on ovh.
Before running this script you need to create a DynHost using the Manager Web
Interface as explained in this guide:
    https://docs.ovh.com/gb/en/domains/hosting_dynhost/
The script exits with a 1 code if errors occur, 75 if the IP on the host is the
same that you are sending. 0 if the change happened correctly.
You can also specify the auth credentials in a separate JSON configuration file

Ruben Di Battista (https://rdb.is)

Usage:
    ovh-dynhost [options] [<hostname>] [<username>] [<password>]

Options:
    -h, --help                  Show this help text
    -d, --debug                 Enable Debug verbosity for logging
    --ip=<ip>                   Override automatically detected public ip
                                    with <ip>. Default retrieved from ipify
    --pub-ip-source=<url>       Override the API url from which to get as a
                                    text response the public IP

    --log-file=<path>           Set a file where to log into. Default logs only
                                    in stdout
    --conf-file=<path>          Specify where to locate the JSON configuration
                                    file. Default in $HOME/.ovh-dynhost.conf

Examples:
    ovh-dynhost home.mydomain.com myusername mypassword (Standard)

    ovh-dynhost --ip=0.0.0.0 home.mydomain.com myusername mypassword
        (Override Public Ip)

    ovh-dynhost --pub-ip-source=http://bot.whatismyipaddress.com \\
    home.mydomain.com myusername mypassword
    (Get public ip from whatismyipaddress.com instead  of ipify.org)

    ovh-dynhost --log-file=ovh.log home.mydomain.com myusername mypassword
        (Log to `ovh.log` file)
"""

import json
import logging
import os
import sys
import requests
import docopt

from ._version import __version__

DEFAULT_PUBLIC_IP_API_URL = 'https://api.ipify.org'
DEFAULT_CONF_PATH = os.path.join(os.getenv('HOME'), '.ovh-dynhost.conf')
OVH_API_ENDPOINT = 'https://www.ovh.com/nic/update'

# EXIT CODES
SAME_IP_ERROR = 75
GENERAL_ERROR = 1


def get_conf(conf_path, hostname=None, username=None,
             password=None):
    global LOGGER

    if not os.path.exists(conf_path):
        LOGGER.warning("No config file found at {conf_path}".format(
            conf_path=conf_path))
        return (hostname, username, password)

    conf_file = open(conf_path, 'r')
    conf = json.load(conf_file)
    conf_file.close()

    if hostname is None:
        hostname = conf['hostname']
    if username is None:
        username = conf['username']
    if password is None:
        password = conf['password']

    return (hostname, username, password)


def main():
    global LOGGER

    # Parse arguments
    args = docopt.docopt(
        __doc__, version=__version__)

    hostname = args['<hostname>']
    username = args['<username>']
    password = args['<password>']
    public_ip_api_url = args['--pub-ip-source']
    logfile = args['--log-file']
    conf_file = args['--conf-file']
    debug = args['--debug']

    if not(conf_file):
        conf_file = DEFAULT_CONF_PATH

    # Logging Configuration
    LOGGER = logging.getLogger('ovh-dynhost')
    logging_level = logging.INFO
    if debug:
        logging_level = logging.DEBUG
    LOGGER.setLevel(logging_level)

    # Stdout Log
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging_level)
    LOGGER.addHandler(console_logger)

    # File Log (if requested)
    if logfile:
        logging.basicConfig(
            filename=logfile,
            level=logging_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        LOGGER.info("Logging to {logfile}".format(logfile=logfile))

    (hostname, username, password) = get_conf(conf_path=conf_file,
                                              hostname=hostname,
                                              username=username,
                                              password=password)

    LOGGER.debug('Hostname {hostname} username {username} '
                 'password {password}'.format(hostname=hostname,
                                              username=username,
                                              password=password))

    if public_ip_api_url:
        url = public_ip_api_url
    else:
        url = DEFAULT_PUBLIC_IP_API_URL

    LOGGER.debug("Retrieving Public IP from:{}".format(url))

    if args['--ip']:
        ip = args['--ip']
    else:
        # Retrieving public IP from web service
        ip = requests.get(url).text

    LOGGER.info("Public IP: {}".format(ip))

    # Building Request
    payload = {
        'myip': ip,
        'system': 'dyndns',
        'hostname': hostname
    }

    headers = {
        'user-agent': 'ovh-dynhost/' + __version__
    }

    authentication = requests.auth.HTTPBasicAuth(username, password)

    # Run Request
    request = requests.Request('GET', url=OVH_API_ENDPOINT, params=payload,
                               headers=headers, auth=authentication).prepare()

    session = requests.Session()
    response = session.send(request).text.lower()

    if "good" in response:
        LOGGER.info("IP successfully updated")
        sys.exit(0)
    elif "nochg" in response:
        LOGGER.debug("Matching same IP.  Not changed")
        sys.exit(SAME_IP_ERROR)
    else:
        LOGGER.error(
            "Error occurred in updating IP. Response from server:{}"
            .format(response))
        sys.exit(GENERAL_ERROR)


if __name__ == '__main__':
    main()
