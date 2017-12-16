#!/usr/bin/env python3
"""
This scripts updates the DynHost configured on your domain registered on ovh.
Before running this script you need to create a DynHost using the Manager Web
Interface as explained in this guide:
    https://www.ovh.com/us/g2024.hosting_dynhost
The script exit with a 1 code if errors occur, 75 if the IP on the host is the
same that you are sending. 0 if the change happened correctly.

Usage:
    ovh-dynhost [options] [<hostname>] [<username>] [<password>]

Options:
    -h, --help                  Show this help text
    --ip=<ip>                   Override automatically detected public ip
                                    with <ip>. Default retrieved from ipify
    --pub-ip-source=<url>       Override the API url from which to get as a
                                    text response the public IP

    --log-file=<path>           Set a file where to log into. Default logs only
                                    in stdout

Examples:
    ovh-dynhost home.mydomain.com myusername mypassword (Standard)

    ovh-dynhost --ip=0.0.0.0 home.mydomain.com myusername mypassword
        (Override Public Ip)

    ovh-dynhost --pub-ip-source=http://bot.whatismyipaddress.com \\
    home.mydomain.com myusername mypassword
    (Get public ip from whatismyipaddress.com instead  of ipify.org)

    ovh-dynhost --log-file=ovh.log home.mydomain.com myusername mypassword
        (Log to `ovh.log` file)


--------------------------------------------------------------------------------

Copyright 2017 Ruben Di Battista <rubendibattista@gmail.com>

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import json
import logging
import os
import sys
import requests
import docopt

VERSION = '0.2'

DEFAULT_PUBLIC_IP_API_URL = 'https://api.ipify.org'
DEFAULT_CONF_PATH = os.path.join(os.getenv('HOME'), '.ovh-dynhost.conf')
OVH_API_ENDPOINT = 'https://www.ovh.com/nic/update'

def get_conf(conf_path=DEFAULT_CONF_PATH, hostname=None, username=None, password=None):
    global LOGGER

    if not os.path.exists(conf_path):
        LOGGER.warning("No config file found at {conf_path}".format(conf_path=conf_path))
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
    args = docopt.docopt(__doc__, version='Ovh DynHost Update Script v'+VERSION)

    hostname = args['<hostname>']
    username = args['<username>']
    password = args['<password>']
    public_ip_api_url = args['--pub-ip-source']
    logfile = args['--log-file']

    # Logging Configuration
    LOGGER = logging.getLogger('ovh-dynhost')
    LOGGER.setLevel(logging.DEBUG)

    # Stdout Log
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.INFO)
    LOGGER.addHandler(console_logger)

    # File Log (if requested)
    if logfile:
        logging.basicConfig(
            filename=logfile,
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        LOGGER.info("Logging to {logfile}".format(logfile=logfile))

    (hostname, username, password) = get_conf(hostname=hostname, 
            username=username, 
            password=password)

    LOGGER.debug('Hostname %s username %s password %s' % (hostname, username, password))
    
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
        'user-agent': 'ovh-dynhost/' + VERSION
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
        sys.exit(75)
    else:
        LOGGER.error(
            "Error occured in updating IP. Response from server:{}"
            .format(response))
        sys.exit(1)

if __name__ == '__main__':
    main()
