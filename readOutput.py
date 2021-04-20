#!/bin/env python3
# 107 entry in output2 is not correct
#output2 entries upto 127 are taken
#output3 156 entry is not correct
#output 7  and output 11 are in the same file output7.bin
import pickle
fileHandler = open("output/output7.bin", 'rb')
while 1:
  try:
    B = pickle.load(fileHandler)
    print(B)
  except:
    break

