#!/bin/bash


controller0="./controllers/controller.py"
controller1="./controllers/controller.py"
observe=1
rest=1

usage(){
	echo "usage: run-controller.h [[-f file]] [[-o]] [[-r]]"
}


while [ "$1" != "" ]; do
	case $1 in
		-f | --file ) shift
			      controller=$1
			      ;;
		-o | --observe-links )
				       observe=0
				       ;;
		-r | --rest ) 
			      rest=0
			      ;;
		* )	      usage
			      exit 1
	esac
	shift
done

if [ "$observe" == "1"  ] && [ "$rest" == "1"  ]; then
	ryu-manager $controller0 ryu.app.ofctl_rest --observe-links
	ryu-manager $controller1 ryu.app.ofctl_rest --observe-link --ofp-tcp-listen-port 6634
elif [ "$observe" == "1" ]; then
	ryu-manager $controller0 --observe-links
	ryu-manager $controller1 --observe-links --ofp-tcp-listen-port 6634
elif [ "$rest" == "1" ]; then
	ryu-manager $controller0 ryu.ap.ofctl_rest
	ryu-manager $controller1 ryu.ap.ofctl_rest --ofp-tcp-listen-port 6634
else
	ryu-manager $controller0
	ryu-manager $controller1 --ofp-tcp-listen-port 6634
fi
