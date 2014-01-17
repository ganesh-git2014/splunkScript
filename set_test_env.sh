#!/bin/bash
# export SPLUNK_HOME="$1"
P4ROOT="/Users/clin/Documents/p4depot/splunk"
BRANCH="$2"

if [ current == "$2" ]; then
	cd "$P4ROOT/current/new_test"
else
    cd "$P4ROOT/branches/$2/new_test"
fi

source setTestEnv "$1"
cd "tests/web/webdriver"