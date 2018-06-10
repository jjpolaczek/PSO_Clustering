#!/usr/bin/env bash
#workon einis

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
   /home/kuba/.virtualenvs/einis/bin/python2.7 textClusterize.py --clusters="$i" --no-retries=1
   #sleep 0.5; echo "$i";
}
N=1
open_sem $N
for ((i=$1;i<=$2;i++)); do
    task $i
    #run_with_lock task $i
    #run_with_lock echo `python textClusterize.py --clusters=$i --no-retries=3 &`
done
