#!/bin/bash
ps_out=`ps -ef | grep rockAtlas | grep -v 'grep' | grep -v $0`
result=$(echo $ps_out | grep "rockAtlas cache")
if [[ "$result" != "" ]];then
    echo "rockAtlas already downloading - moving on"
else
    echo "rockAtlas not downloading - kick starting"i
    /home/dry/.conda/envs/rockAtlas/bin/rockAtlas cache 5
fi
