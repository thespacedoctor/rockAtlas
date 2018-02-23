#!/bin/bash
ps_out=`ps -ef | grep rockAtlas | grep -v 'grep' | grep -v $0`
result=$(echo $ps_out | grep -E "rockAtlas orbfit|rockAtlas pyephem")
if [[ "$result" != "" ]];then
    echo "rockAtlas already generating orbfit positions - moving on"
else
    echo "rockAtlas not generating orbfit positions - kick starting"
    /home/dry/.conda/envs/rockAtlas/bin/rockAtlas orbfit
fi
