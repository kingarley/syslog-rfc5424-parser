#!/usr/bin/env python

from __future__ import print_function

import argparse
import socket
import os
import sys
import json

from syslog_rfc5424_parser import SyslogMessage, ParseError

def main():
    host='0.0.0.0'

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--protocol', required=True,
            help='Protocol: udp/tcp')
    parser.add_argument('--port', required=True,
                        help='Port number')
    args = parser.parse_args()

    protocol = args.protocol.lower()
    if protocol == 'udp':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    elif protocol == 'tcp':
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
        print("error, protocol not UDP or TCP")
        sys.exit(1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    port = int(args.port)
    print("Listening on %s %s:%s" % (protocol, host, port))
    s.bind((host, port))

    if protocol == 'udp':
        connection = s
    else:
        s.listen(1)
        # Wait for a connection
        print('waiting for a connection')
        connection, client_address = s.accept()
        print('accepted connection from: %s %s'%(client_address))
    while True:
        message = connection.recv(4096)
        # Technically, messages are only UTF-8 if they have a BOM; otherwise they're binary. However, I'm not
        # aware of any Syslog servers that handle that. *shrug*
        message = message.decode('utf-8')
        try:
            message = SyslogMessage.parse(message)
            print(json.dumps(message.as_dict()))
        except ParseError as e:
            print(e, file=sys.stderr)

if __name__ == '__main__':
    sys.exit(main())
