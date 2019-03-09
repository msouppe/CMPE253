#!/bin/bash

#topology="./topologies/mn_ft.py"
#topo="ft"
topology="./topologies/fat_tree.py"

usage(){
	echo "usage: run.sh [[-f file]] [[-t topo]]"
}


while [ "$1" != "" ]; do
	case $1 in
		-f | --file ) shift
			      topology=$1
			      ;;
		-t | --topo ) shift
			      topo=$1
			      ;;
		* )  	      usage
			      exit 1

	esac
	shift
done	


#sudo mn --custom $topology --topo $topo --mac --switch ovs --controller remote
sudo python $topology
sudo mn -c; clear
exit 0
