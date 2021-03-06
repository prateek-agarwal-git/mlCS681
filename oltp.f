set $dir=/tmp
set $iosize=16k
set $nshadows=10
set $ndbwriters=20
set $usermode=400000
set $filesize=10m
set $memperthread=1m
set $workingset=0
set $logfilesize=10m
set $nfiles=10
set $nlogfiles=10
set $directio=1
define fileset name=datafiles,path=$dir,size=$filesize,entries=$nfiles,dirwidth=1024,prealloc=100,reuse
define fileset name=logfile,path=$dir,size=$logfilesize,entries=$nlogfiles,dirwidth=1024,prealloc=100,reuse


define process name=lgwr,instances=1
{
    thread name=lgwr,memsize=$memperthread,useism
  {
    flowop aiowrite name=lg-write,filesetname=logfile,
       iosize=256k,random,directio=$directio,dsync    flowop aiowait name=lg-aiowait

flowop semblock name=lg-block,value=3200,highwater=1000
   }
  }define process name=dbwr,instances=$ndbwriters
 {
 thread name=dbwr,memsize=$memperthread,useism
 {
 flowop aiowrite name=dbwrite-a,filesetname=datafiles,
    iosize=$iosize,workingset=$workingset,random,iters=100,opennext,directio=$directio,dsync
    flowop hog name=dbwr-hog,value=10000
 flowop semblock name=dbwr-block,value=1000,highwater=2000
 flowop aiowait name=dbwr-aiowait
 }
 }
 define process name=shadow,instances=$nshadows
{
 thread name=shadow,memsize=$memperthread,useism

{
   flowop read name=shadowread,filesetname=datafiles,
   
 iosize=$iosize,workingset=$workingset,random,opennext,directio=$directio

    flowop hog name=shadowhog,value=$usermode
     flowop sempost name=shadow-post-lg,value=1,target=lg-block,blocking
    flowop sempost name=shadow-post-dbwr,value=1,target=dbwr-block,blocking
    flowop eventlimit name=random-rate
    }
}
run 30