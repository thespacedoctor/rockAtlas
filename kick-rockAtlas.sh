#!/bin/bash
ps_out=`ps -ef | grep rockAtlas | grep -v 'grep' | grep -v $0`
result=$(echo $ps_out | grep "rockAtlas")
if [[ "$result" != "" ]];then
    echo "Running"
else
    echo "Not Running"
fi
