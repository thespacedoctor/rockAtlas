#!/bin/bash
ps_out=`ps -ef | grep rockAtlas | grep -v 'grep' | grep -v $0`
result=$(echo $ps_out | grep "rockAtlas")
if [[ "$result" != "" ]];then
    echo "rockAtlas already running - moving on"
else
    echo "rockAtlas not running - kick starting"i
    /home/dry/.conda/envs/rockAtlas/bin/rockAtlas cycle 5
fi
