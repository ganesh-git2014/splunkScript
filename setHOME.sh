#!/usr/bin/bash

if [ -d "/Users/clin/splunk/$1" ]; then
    export SPLUNK_HOME="/Users/clin/splunk/$1"
else
    echo "Directory \"/Users/clin/splunk/$1\" does not exist"
    return
fi

p4dir="/Users/clin/Documents/p4depot/splunk"
if [ current == "$1" ]; then
    if [ -d "$p4dir/$1" ]; then
	export SPLUNK_SOURCE="$p4dir/$1"
    else
	echo "Directory \"$p4dir/$1\" does not exist"
	return
    fi
else
    if [ -d "$p4dir/branches/$1" ]; then
	export SPLUNK_SOURCE="$p4dir/branches/$1"
    else
	echo "Directory \"$p4dir/branches/$1\" does not exist"
	return
    fi
fi

# set test enviroment
cd "$SPLUNK_SOURCE/test"
. setTestEnv
clear
