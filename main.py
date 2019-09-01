#!/usr/bin/env python3
import statistics
import math
#--------------------------------------------------
#**Part 1:**
#1:Check DB Size + LRU DB Management
#2:Packet_out + Check if flow-entry exist
#3:Update data(Time_stamp, idle_timeout)
#4:Check-interval & Install determination
#5:Check TCAM Space Usage
#6:Install Flow Entry
#**End of Part 1**
#--------------------------------------------------
#
#
#
#
#
#
class db_content:
    def __init__(self):
            self.timestamp    = list()
            self.idle_timeout = list()
            self.interval     = list() 
            self.active_flag  = none

db = {} #db init as dict

#------------------------------------------------
#       Places to Declare Variable              #
#------------------------------------------------
db_threshold = 5000 #key的數量設定爲5000
Packet_out   = 0      #一共處理了多少封包
TCAM_Max     = 2000     #TCAM能存儲2000條Flow_entries
TCAM_Current = 0    #目前TCAM的佔用情況
#-----------------------------------------------#
#                                               #
#                 Part 1 & 2                    #
#                     CP                        #
#-----------------------------------------------#
def PacketProcessing():
    
    #取出封包中的欄位 --> SrcIP + DstIP 做HASH
    flow_id = hash(SrcIP + DstIP)
    return flow_id
    

def db_LRU(dict db):
    #Sorting according to last_timestamp
    #Delete least recently use record from db
    #return db after deletion
    return db


def CheckDB(dict db):
    #DB size > threshold ?
    if(db.size() > db_threshold):
        db_LRU(db)
        CheckDBSize(db)
    else:
        Packet_out += 1
        #Maintain packet out counter
            

def CheckFlowExist_DB(String key, dict db): #Flow entry in DB ?
    #To check if DB has this flow record
    if(flow_id in db = True):
        UpdateData(db）#更新timestamp
    else:
        #Add record to DB
        db[flow_id] = db_content()#能否用hash當key存？
        db[flow_id].timestamp.append(time.time()) #添加新的時間記錄


def UpdateData(dict db,float flow_id, float idle_timeout = 7.0): #更新Time Stamp以及idle_timeout
    db[flow_id].idle_timeout.append(idle_timeout)  #若沒有帶值進來，則使用預設7s
    db[flow_id].timestamp.append(time.time())      #記錄最近Time Stamp

def CheckInterval(dict db,float flow_id):
    tmp = db[flow_id].timestamp[len(db[flow_id].timestamp) - 1] #last time stamp
    print tmp
    if(time.time() - tmp < 11):
        while(TCAM_Current >= TCAM_Max - 1 ):
            #這條插入後會導致滿，則進行刪除
            TCAM_Current = DeleteFlowEntry(db, TCAM_Current)

        if(TCAM_Current < TCAM_Max):
            #install
            TCAM_Current = TCAM_Current + 1 
            #更新TCAM用量
            db[flow_id].interval.clear()
            #Clear interval list
            db[flow_id].active_flag = True
            #在DB中對已插入的flow做標記
        else:
            #進行Flow Mod
            DeleteFlowEntry(db, TCAM_Current)
            

    else:
        print("Cancel installaion of :"flow_id) #Print出取消插入的flow id

def DeleteFlowEntry(dict db, int TCAM_Current):
    #找到DB中有active flag之最不常用的flow
    DB SORT #需要根據timestamp排序，剔除最後的記錄
    #排序後進行刪除
    TCAM_Current = TCAM_Current - 1
    return TCAM_Current

def ProcessingRemovalMessage(dict db, float flow_id, float duration, int packet_count):
    #update time stamp
    db[flow_id].timestamp.append(time.time())
    #mark flow as inactive
    db[flow_id].active_flag = False
    #free tcam spaces
    TCAM_Current = TCAM_Current - 1 
    #Calculate time interval based last two timestamp
    interval = db[flow_id].timestamp(len(db[flow_id].timestamp) - 1) - db[flow_id].timestamp(len(db[flow_id].timestamp) - 2)
    #update interval
    db[flow_id].interval.append(interval)

    #check if len(interval) >= 6 --->Threshold 3
    if(len(db[flow_id].interval) >= 6):
        #calculate mean through interval list
        mean = statistics.mean(db[flow_id].interval)
        #Calculate variance through interval list
        vairance = statistics.variance(db[flow_id].interval)
        #get new idle timeout through 柴比雪夫
        new_timeout = Chebyshev(mean, variance)
        #update data to db
        UpdateData(db, flow_id, new_timeout)

#------------------------------------------------
#                                               #
#                   Part 3                      #
#                   Switch                      #
#------------------------------------------------




if __name__ == '__main__':
    print