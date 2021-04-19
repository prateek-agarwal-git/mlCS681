#!/bin/env python3
#iosize, nshadows, dbwriters, usermode, filesize, logfilesize, nlogfiles, 
# Define a datafile and logfile
import sys

s = "set $dir=/tmp\nset $runtime=30\nset $iosize=2k\nset $nshadows=50\n"
s+= "set $ndbwriters=10\nset $usermode=200000\nset $filesize=10m\n"
s+="set $memperthread=1m\nset $workingset=0\n"
s+="set $logfilesize=10m\nset $nfiles=10\nset $nlogfiles=10\nset $directio=1\n"
s+="define fileset name=datafiles,path=$dir,size=$filesize,entries=$nfiles,dirwidth=1024,prealloc=100,reuse\n"
s+="define fileset name=logfile,path=$dir,size=$logfilesize,entries=$nlogfiles,dirwidth=1024,prealloc=100,reuse\n"
s+="\n\ndefine process name=lgwr,instances=1\n{\n    thread name=lgwr,memsize=$memperthread,useism\n  {\n    "
s+="flowop aiowrite name=lg-write,filesetname=logfile,\n       iosize=256k,random,directio=$directio,dsync"
s+="    flowop aiowait name=lg-aiowait\n\nflowop semblock name=lg-block,value=3200,highwater=1000\n   }\n  }"
s+="define process name=dbwr,instances=$ndbwriters\n {\n thread name=dbwr,memsize=$memperthread,useism\n"
s+=" {\n flowop aiowrite name=dbwrite-a,filesetname=datafiles,\n    iosize=$iosize,workingset=$workingset,"
s+="random,iters=100,opennext,directio=$directio,dsync\n   "
s+=" flowop hog name=dbwr-hog,value=10000\n"
s+=" flowop semblock name=dbwr-block,value=1000,highwater=2000\n"
s+=" flowop aiowait name=dbwr-aiowait\n }\n }\n"
s+=" define process name=shadow,instances=$nshadows\n{\n thread name=shadow,memsize=$memperthread,useism\n"
s+="\n{\n   flowop read name=shadowread,filesetname=datafiles,\n   "
s+="\n iosize=$iosize,workingset=$workingset,random,opennext,directio=$directio\n"
s+="\n    flowop hog name=shadowhog,value=$usermode\n    "
s+=" flowop sempost name=shadow-post-lg,value=1,target=lg-block,blocking\n   "
s+=" flowop sempost name=shadow-post-dbwr,value=1,target=dbwr-block,blocking\n   "
s+=" flowop eventlimit name=random-rate\n    }\n}\n"
s+="run 60"
print(s)