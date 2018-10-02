#!/bin/bash

SQLITE="/usr/bin/sqlite3"
if [ -n $OPENVPN_DBFILE ]; then
	OPENVPN_DBFILE="ovpn_session.db"
fi
if [ -n $OPENVPN_MAXCONN_PER_USER ]; then
	OPENVPN_MAXCONN_PER_USER=3
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

create_table(){

}

# db_query 'insert into a123 (number) values (1);'
case $script_type in
	up)
		create_table
		;;
	client-connect)
		;;
	learn-address)
		;;
	client-disconnect)
		;;
	down)

