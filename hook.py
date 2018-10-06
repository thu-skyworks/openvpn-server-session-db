#!/usr/bin/env python3

import os
from sqlalchemy import create_engine, MetaData, Table, Column, \
    String, Time, Interval, func
from sqlalchemy.sql import select, and_
from sqlalchemy.dialects.mysql import SMALLINT, INTEGER
import json
import logging
from datetime import datetime, timedelta

if __name__ == '__main__':
    logger = logging.getLogger('main')
    logging.basicConfig(level=logging.DEBUG)

    with open(os.getcwd() + '/config.json') as f:
        config = json.load(f)

    engine = create_engine(config['dburl'], echo=True)
    metadata = MetaData()
    vpnsessions = Table('sessions', metadata,
                        Column('session_id', INTEGER(unsigned=True),
                               primary_key=True,
                               autoincrement=True),
                        Column('daemon_start_time', Time),
                        Column('username', String(32)),
                        Column('ip', String(64)),
                        Column('port', SMALLINT(unsigned=True)),
                        Column('connect_time', Time),
                        # NULL if still connected:
                        Column('session_length', Interval, nullable=True),
                        Column('bytes_to_client', INTEGER(unsigned=True)),
                        Column('bytes_from_client', INTEGER(unsigned=True)),
                        Column('client_os', String(128)),
                        Column('client_ssl', String(32)),
                        Column('client_ver', String(32))
                        )
    metadata.create_all(engine)

    daemonStartTime = datetime.fromtimestamp(
        int(os.getenv('daemon_start_time')))
    scriptType = os.envron.get('script_type')

    if scriptType == 'up':
        pass
    elif scriptType == 'down':
        pass
    elif scriptType == 'client-connect':
        username = os.getenv('username')
        ip = os.getenv('trusted_ip')
        port = int(os.getenv('trusted_port'))
        connectTime = datetime.fromtimestamp(
            int(os.getenv('time_unix')))
        stmt = select([
            func.count(vpnsessions.c.session_id)]).\
            where(
                and_(
                    vpnsessions.c.username == username,
                    vpnsessions.c.daemon_start_time == daemonStartTime,
                    vpnsessions.c.session_length is None
                )
            )
        conn = engine.connect()
        print(conn.execute(stmt).fetchone())
        ins = vpnsessions.insert()
        pass
    elif scriptType == 'client-disconnect':
        sessionLength = timedelta(
            seconds=int(os.getenv('time_duration')))
        bytesToClient = int(os.getenv('bytes_sent'))
        bytesFromClient = int(os.getenv('bytes_received'))
        pass
    elif scriptType == 'learn-address':
        pass
