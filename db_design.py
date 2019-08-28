#!/usr/bin/env python3
# coding=utf-8
import time
import math

class event: #需要什麼資料結構，直接誒定義於此
  def __init__(self):
    self.timestamp    = list() #init as dict
    self.idle_timeout = list() #init as dict
    self.active_flag  = 0

db = dict()

TimeStamp = list()
idle_timeout = list()

#Time_data = dict(zip(TimeStamp,idle_timeout))

#Time_data = dict()

for k in range(1,11):
  db[k] = event() #直接將class引入db的設計中，在class中定義好後續需要什麼欄位
  db[k].timestamp.append(time.time())
  db[k].timestamp.append(time.time()+math.sqrt(k*math.pi))
  db[k].idle_timeout.append(math.sqrt(k))
  if(int(k*k/math.sqrt(k)) % 2 != 0):
      db[k].active_flag = 1
  else:
      db[k].active_flag = 0
  

#db = dict(zip(db,Time_data ))

#print(Time_data);
#print(db);
#for key in db: #直接使用db遍歷輸出
 #   print("Flow hash ID", "TimeStamp", "Idle_TImeout", "ActiveFlag")
  #  print(key, db[key].timestamp, db[key].idle_timeout, db[key].active_flag, "\n")
length = len(db[7].timestamp)
print(db[7].timestamp[length-1], db[7].timestamp[length-2])
print(db[7].timestamp[0],"/n",db[7].timestamp[1])

