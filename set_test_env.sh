#!/bin/bash
P4ROOT="/Users/clin/Documents/p4depot/splunk"
BRANCH="$1"

if [ current == "$1" ]; then
	testdir="$P4ROOT/current/new_test"
else
    testdir="$P4ROOT/branches/$1/new_test"
fi

cd $testdir

splunks=(`findsplunk`)
total=${#splunks[@]}
if [ 1 == $total ]; then
	if [ 'bubbles' == "$1" ]; then
		source setTestEnv ${splunks[0]}
	else
		source setTestEnv -s ${splunks[0]}
	fi
else
	echo "Which splunk do you want to run test?"
	for (( i=0; i<=$(( $total -1 )); i++ ))
	do
		echo "$i) ${splunks[$i]}"
	done
	read index

	if [ 'bubbles' == "$1" ]; then
		source setTestEnv "${splunks[$index]}"
	else
		source setTestEnv -s "${splunks[$index]}"
	fi
fi

alias cdt="cd $testdir/tests/web/webdriver"
cdt