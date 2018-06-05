#!/bin/bash

if [ -n $script_type ]; then
	echo Script $script_type called.
	echo $@ > $script_type.txt
	printenv >> $script_type.txt
fi
