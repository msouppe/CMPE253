#!/bin/bash
#! /bin/bash

# Kill Java process

# Determine the pid
PID=`ps -C java -o pid=`

kill -9 $PID

kill $(ps aux | grep controller | awk '{print $2}') 

controller0="/home/pranav/ofworkspace/CMPE253/controllers/controller.py"
controller1="/home/pranav/ofworkspace/CMPE253/controllers/controller.py"
controller2="/home/pranav/ofworkspace/CMPE253/controllers/controller.py"
controller3="/home/pranav/ofworkspace/CMPE253/controllers/controller.py"

ryu_path=/home/parallels/ryu/bin/ryu-manager
jar_path=/home/pranav/ofworkspace/CMPE253/controllers
dir=/home/pranav/ofworkspace/CMPE253

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
#Starting jar files
echo "STARTING BFT SMART SERVERS"
java -jar $jar_path/sdnstore.jar -server 0  /home/pranav/ofworkspace/CMPE253/controllers/c0/nib.txt &
sleep 2
java -jar $jar_path/sdnstore.jar -server 1  /home/pranav/ofworkspace/CMPE253/controllers/c1/nib.txt &
sleep 2
java -jar $jar_path/sdnstore.jar -server 2  /home/pranav/ofworkspace/CMPE253/controllers/c2/nib.txt &
sleep 2
java -jar $jar_path/sdnstore.jar -server 3  /home/pranav/ofworkspace/CMPE253/controllers/c3/nib.txt &
sleep 2
java -jar $jar_path/py4jclient.jar 4 9500 &
sleep 2
java -jar $jar_path/py4jclient.jar 5 9502 &
sleep 2
java -jar $jar_path/py4jclient.jar 6 9504 &
sleep 2
java -jar $jar_path/py4jclient.jar 7 9506 &
sleep 2



if [ "$observe" == "1"  ] && [ "$rest" == "1"  ]; then
	sudo $ryu_path $controller0 ryu.app.ofctl_rest --observe-links --config-file $dir/controllers/c0/param.conf &
	sleep 2
	sudo $ryu_path $controller1 ryu.app.ofctl_rest --observe-link --ofp-tcp-listen-port 6634 --config-file $dir/controllers/c1/param.conf &
	sleep 2
	sudo $ryu_path $controller2 ryu.app.ofctl_rest --observe-link --ofp-tcp-listen-port 6635 --config-file $dir/controllers/c2/param.conf &
	sleep 2
	sudo $ryu_path $controller3 ryu.app.ofctl_rest --observe-link --ofp-tcp-listen-port 6636 --config-file $dir/controllers/c3/param.conf &
elif [ "$observe" == "1" ]; then
	sudo $ryu_path $controller0 --observe-links --config-file $dir/controllers/c0/param.conf &
	sleep 2
	sudo $ryu_path $controller1 --observe-links --ofp-tcp-listen-port 6634 --config-file $dir/controllers/c1/param.conf &
	sleep 2
	sudo $ryu_path $controller2 --observe-links --ofp-tcp-listen-port 6635 --config-file $dir/controllers/c2/param.conf &
	sleep 2
	sudo $ryu_path $controller3 --observe-links --ofp-tcp-listen-port 6636 --config-file $dir/controllers/c3/param.conf &
elif [ "$rest" == "1" ]; then
	sudo $ryu_path $controller0 ryu.ap.ofctl_rest --config-file $dir/controllers/c0/param.conf &
	sudo $ryu_path $controller1 ryu.ap.ofctl_rest --ofp-tcp-listen-port 6634 --config-file $dir/controllers/c1/param.conf &
	sudo $ryu_path $controller2 ryu.ap.ofctl_rest --ofp-tcp-listen-port 6635 --config-file $dir/controllers/c2/param.conf &
	sudo $ryu_path $controller3 ryu.ap.ofctl_rest --ofp-tcp-listen-port 6636 --config-file $dir/controllers/c3/param.conf &
else
	sudo $ryu_path $controller0 --config-file $dir/controllers/c0/param.conf &
	sudo $ryu_path $controller1 --ofp-tcp-listen-port 6634 --config-file $dir/controllers/c1/param.conf &
	sudo $ryu_path $controller2 --ofp-tcp-listen-port 6635 --config-file $dir/controllers/c2/param.conf &
    sudo $ryu_path $controller3 --ofp-tcp-listen-port 6636 --config-file $dir/controllers/c3/param.conf &
fi
