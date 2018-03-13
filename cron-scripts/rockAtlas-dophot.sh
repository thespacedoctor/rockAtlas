#!/bin/bash
ps_out=`ps -ef | grep rockAtlas | grep -v 'grep' | grep -v $0`
result=$(echo $ps_out | grep -E "rockAtlas dophot")
if [[ "$result" != "" ]];then
    echo "rockAtlas already parsing dophot measurements - moving on"
else
    echo "rockAtlas not parsing dophot measurements - kick starting"
    /home/dry/.conda/envs/rockAtlas/bin/rockAtlas dophot
fi
