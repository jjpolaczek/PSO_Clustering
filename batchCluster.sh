#!/usr/bin/env bash


#for ((i=$1;i<=$2;i++)); do
#    echo `python textClusterize.py --clusters=$i --no-retries=3`
#done

open_sem(){
    mkfifo pipe-$$
    exec 3<>pipe-$$
    rm pipe-$$
    local i=$1
    for((;i>0;i--)); do
        printf %s 000 >&3
    done
}
run_with_lock(){
    local x
    read -u 3 -n 3 x && ((0==x)) || exit $x
    (
    "$@"
    printf '%.3d' $? >&3
    )&
}
task(){
    python textClusterize.py --clusters="$i" --no-retries=3
   #sleep 0.5; echo "$1";
}
N=6
open_sem $N
for ((i=$1;i<=$2;i++)); do
    run_with_lock task $i
    #run_with_lock echo `python textClusterize.py --clusters=$i --no-retries=3 &`
done