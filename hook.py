#!/usr/bin/env python3

import os
from sqlalchemy import create_engine, MetaData, Table, Column, \
    String, DateTime, func
from sqlalchemy.sql import select, and_
from sqlalchemy.dialects.mysql import SMALLINT, INTEGER
import json
import logging
from datetime import datetime, timedelta
import argparse
import sys

if __name__ == '__main__':
    logger = logging.getLogger('main')
    parser = argparse.ArgumentParser(description='OpenVPN Server Hook')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Additional arguments: ' + ' '.join(args.args))
        sqlEcho = True
    else:
        logging.basicConfig(level=logging.INFO)
        sqlEcho = False

    with open(os.getcwd() + '/config.json') as f:
        config = json.load(f)

    engine = create_engine(config['dburl'], echo=sqlEcho)
    metadata = MetaData()
    vpnsessions = Table('sessions', metadata,
                        Column('session_id', INTEGER(unsigned=True),
                               primary_key=True,
                               autoincrement=True),
                        Column('daemon_start_time', DateTime),
                        Column('username', String(32)),
                        Column('ip', String(64)),
                        Column('port', SMALLINT(unsigned=True)),
                        Column('connect_time', DateTime),
                        Column('vpn_ip', String(15)),
                        # NULL if still connected:
                        Column('disconnect_time', DateTime,
                               nullable=True),
                        Column('bytes_to_client', INTEGER(unsigned=True)),
                        Column('bytes_from_client', INTEGER(unsigned=True)),
                        Column('client_os', String(128)),
                        Column('client_ssl', String(32)),
                        Column('client_ver', String(32)),
                        Column('client_gui_ver', String(32)),
                        Column('client_device_name', String(128))
                        )
    metadata.create_all(engine)

    scriptType = os.getenv('script_type')

    if scriptType == 'up':
        pass
    elif scriptType == 'down':
        pass
    elif scriptType == 'client-connect':
        if os.getenv('IV_PLAT') is None:  # client didn't push peer info
            with open(args.args[0], 'w') as f:
                f.write('disable')
            logger.info("Client didn't push peer info, rejecting.")
            sys.exit(0)
        daemonStartTime = datetime.fromtimestamp(
            int(os.getenv('daemon_start_time')))
        username = os.getenv('username')
        ip = os.getenv('trusted_ip')
        if ip is None:
            ip = os.getenv('trusted_ip6')
        vpnIP = os.getenv('ifconfig_pool_remote_ip')
        clientOS = ' '.join(filter(None, [os.getenv('IV_PLAT'),
                                          os.getenv('IV_PLAT_VER')]))
        clientSSL = os.getenv('IV_SSL')
        clientVer = os.getenv('IV_VER')
        clientGUIVer = os.getenv('IV_UI_VER')
        clientDeviceName = os.getenv('UV_DeviceName')
        port = int(os.getenv('trusted_port'))
        connectTime = datetime.fromtimestamp(int(os.getenv('time_unix')))
        stmt = select([
            func.count(vpnsessions.c.session_id)]).\
            where(
                and_(
                    vpnsessions.c.username == username,
                    vpnsessions.c.daemon_start_time == daemonStartTime,
                    vpnsessions.c.disconnect_time.__eq__(None)
                )
            )
        conn = engine.connect()
        connectedSessions = conn.execute(stmt).fetchone()[0]
        logger.debug("The user has {} running sessions.".
                     format(connectedSessions))
        if connectedSessions >= config['max_sessions_per_user']:
            with open(args.args[0], 'w') as f:
                f.write('disable')
            logger.info("Maximum sessions for user " + username +
                        " reached, authentication rejected.")
            sys.exit(0)
        ins = vpnsessions.insert().values(
            daemon_start_time=daemonStartTime,
            username=username,
            ip=ip,
            port=port,
            connect_time=connectTime,
            vpn_ip=vpnIP,
            client_os=clientOS,
            client_ssl=clientSSL,
            client_ver=clientVer,
            client_gui_ver=clientGUIVer,
            client_device_name=clientDeviceName
        )
        logger.debug("Creating session info: daemon start time {}, VPN IP {}.".
                     format(daemonStartTime, vpnIP))
        conn.execute(ins)
        pass
    elif scriptType == 'client-disconnect':
        daemonStartTime = datetime.fromtimestamp(
            int(os.getenv('daemon_start_time')))
        connectTime = datetime.fromtimestamp(int(os.getenv('time_unix')))
        sessionLength = timedelta(seconds=int(os.getenv('time_duration')))
        bytesToClient = int(os.getenv('bytes_sent'))
        bytesFromClient = int(os.getenv('bytes_received'))
        vpnIP = os.getenv('ifconfig_pool_remote_ip')
        stmt = vpnsessions.update().\
            where(
                and_(
                    vpnsessions.c.daemon_start_time == daemonStartTime,
                    vpnsessions.c.disconnect_time.__eq__(None),
                    vpnsessions.c.vpn_ip == vpnIP
                )
            ).\
            values(disconnect_time=connectTime + sessionLength,
                   bytes_to_client=bytesToClient,
                   bytes_from_client=bytesFromClient)
        logger.debug("Terminating session: daemon start time {}, VPN IP {}.".
                     format(daemonStartTime, vpnIP))
        conn = engine.connect()
        conn.execute(stmt)
        pass
    elif scriptType == 'learn-address':
        pass
