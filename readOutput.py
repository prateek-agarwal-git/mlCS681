#!/bin/env python3
import pickle
fileHandler = open("output/output1.bin", 'rb')
while 1:
  try:
    B = pickle.load(fileHandler)
    print(B)
  except:
    break

