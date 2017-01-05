#!/usr/bin/env python
"""
This scripts updates the DynHost configured on your domain registered on ovh.
Before running this script you need to create a DynHost using the Manager Web
Interface as explained in this guide:
    https://www.ovh.com/us/g2024.hosting_dynhost
The script exit with a 1 code if errors occur, 75 if the IP on the host is the
same that you are sending. 0 if the change happened correctly.

Usage:
    ovh-dynhost [options] <hostname> <username> <password>

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

import docopt
import logging
import requests
import sys

VERSION = '0.1'

DEFAULT_PUBLIC_IP_API_URL = 'https://api.ipify.org'
OVH_API_ENDPOINT = 'https://www.ovh.com/nic/update'

if __name__ == '__main__':
    # Parse arguments
    args = docopt.docopt(__doc__, version='Ovh DynHost Update Script v'+VERSION)

    hostname = args['<hostname>']
    username = args['<username>']
    password = args['<password>']
    public_ip_api_url = args['--pub-ip-source']
    logfile = args['--log-file']

    # Logging Configuration
    logger = logging.getLogger('ovh-dynhost')
    logger.setLevel(logging.DEBUG)

    # Stdout Log
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.INFO)
    logger.addHandler(console_logger)

    # File Log (if requested)
    if logfile:
        logging.basicConfig(
            filename=logfile,
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger.info("Logging to {logfile}".format(logfile=logfile))

    if public_ip_api_url:
        url = public_ip_api_url
    else:
        url = DEFAULT_PUBLIC_IP_API_URL

    logger.debug("Retrieving Public IP from:{}".format(url))

    if args['--ip']:
        ip = args['--ip']
    else:
        # Retrieving public IP from web service
        ip = requests.get(url).text

    logger.info("Public Ip: {}".format(ip))

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
    r = requests.Request('GET', url=OVH_API_ENDPOINT, params=payload,
                         headers=headers, auth=authentication)
    r = r.prepare()

    s = requests.Session()
    response = s.send(r).text.lower()

    if "good" in response:
        logger.info("IP successfully updated")
        sys.exit(0)
    elif "nochg" in response:
        logger.debug("Matching same IP.  Not changed")
        sys.exit(75)
    else:
        logger.error(
            "Error occured in updating IP. Response from server:{}"
            .format(response))
        sys.exit(1)
