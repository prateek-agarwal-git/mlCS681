#!/bin/env python3
import os
import csv
import pickle
def filebenchFileGenerator(shadows, dbwriters, iosize, cycles,filename):
  s = "set $dir=/tmp\nset $iosize="
  s+=iosize
  s+="\nset $nshadows="
  s+=shadows+"\n"
  s+= "set $ndbwriters="
  s+=dbwriters+"\nset $usermode="+cycles+"\nset $filesize=10m\n"
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
  s+="run 30"
  f = open(filename, 'w')
  f.write(s)
  f.close()
print("first set va_space to 0. run echo0va_space.sh . exit from root mode.")
os.system("sudo -s")
print("switching off hyperthreading")
os.system("sudo ./t.sh")
cpu=["0.5","1","1.5","2"]
memory=["128m", "256m", "512m", "1g"]
nshadows=["10", "30", "50", "70"]
ndbwriters= ["5", "10","15", "20"]
iosizes=["2k", "16k","256k", "512k"]
usermode=["100000","200000", "400000","800000"]  
totalIterations = 4**6
cpuindex = 2 
#ndbwriters = 40 did not work
#filebenchFileGenerator(nshadows[1], ndbwriters[1], iosizes[0], usermode[3],"oltp2123.f")
#filebenchFileGenerator("30", "40", "512k", "800000","oltp.f")
#t = "sudo ./combined.sh " + "0.5"+ " " + "256m"+ " " + "oltp.f" 
#os.system(t)
#exit(0)
output = []
currentIterations=0
for m in memory[:1]:
  for shadow in nshadows:
    for dbwriter in ndbwriters:
      for iosize in iosizes:
        for cycles in usermode:
            try:
              outputFileHandler = open("output/output9.bin",'ab')
              filebenchFileGenerator(shadow, dbwriter, iosize, cycles,"oltp.f")
              t = "sudo ./combined.sh " + cpu[cpuindex]+ " " + m+ " " + "oltp.f" + " > " + "results.out"
              os.system(t)
              f = open("results.out", 'r')
              content = f.readlines()
              if (len(content) >0):
                print(content[-2])
              lines = content[-2].split()
              #NumberOps =lines[-8]
              #ReadsWrites = lines[-4]
              latency = lines[-1][:-5]
              throughputMBPS = lines[-2][:-4]
              throughputOPPS = lines[-6]
              row = [cpu[cpuindex],m,shadow, dbwriter,iosize,cycles , throughputOPPS, throughputMBPS, latency]
              currentIterations+=1
              print(currentIterations)
              f.close() 
              #output.append(row) 
              pickle.dump(row,outputFileHandler)
              outputFileHandler.close() 
            except:
              pass
 
   
 
