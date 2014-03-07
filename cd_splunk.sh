#!/bin/bash

splunks=(`findsplunk`)
total=${#splunks[@]}
if [ 1 == $total ]; then
	cd ${splunks[0]}
else
	echo "Which splunk do you want to run test?"
	for (( i=0; i<=$(( $total -1 )); i++ ))
	do
		echo "$i) ${splunks[$i]}"
	done
	read index
	cd "${splunks[$index]}"
fi