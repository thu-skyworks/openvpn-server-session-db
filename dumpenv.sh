#!/bin/bash

if [ -n $script_type ]; then
	echo Script $script_type called.
	printenv > $script_type.txt
fi
