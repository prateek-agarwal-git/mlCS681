#!/bin/env python3
# 107 entry in output2 is not correct
#output2 entries upto 127 are taken
#output3 156 entry is not correct
import pickle
fileHandler = open("output/output3.bin", 'rb')
while 1:
  try:
    B = pickle.load(fileHandler)
    print(B)
  except:
    break

