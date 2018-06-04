#!/bin/bash

SQLITE="/usr/bin/sqlite3"
if [ -n $OPENVPN_DBFILE ]; then
	OPENVPN_DBFILE="ovpn_session.db"
fi

db_query(){
	result=$($SQLITE $OPENVPN_DBFILE "$1" 2>&1)
	if [ $? -ne 0 ]; then
		echo Error executing SQL \
			\""$(echo "$1" | tr -d "\n")"\". $result 1>&2
		return 1
	else
		echo $result
	fi
	return 0
}

# db_query 'insert into a123 (number) values (1);'
