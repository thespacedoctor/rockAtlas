#!/bin/bash
ps_out=`ps -ef | grep rockAtlas | grep -v 'grep' | grep -v $0`
result=$(echo $ps_out | grep "rockAtlas pyephem")
if [[ "$result" != "" ]];then
    echo "rockAtlas already generating pyephem snapshots - moving on"
else
    echo "rockAtlas not generating pyephem snapshots - kick starting"
    /home/dry/.conda/envs/rockAtlas/bin/rockAtlas pyephem
fi
