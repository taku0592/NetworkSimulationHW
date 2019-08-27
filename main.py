#!/usr/bin/env python3

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
int db_threshold = 5000;
int Packet_out = 0;
String key = null;

def 
def db_LRU(dict db)

def CheckDBSize(dict db):
    if(db.size() > db_threshold):
        db_LRU(db)
        CheckDBSize(db)
    else:
        Packet_out += 1;
        #After if-else, update packet-out counter
            
def db_LRU(dict db):
    #Delete least recently use record from db
    #return db after deletion
    return db

def CheckFlowExist_DB(String key, dict db):
    #To check if DB has this flow record
    if(hash(key) in db = True):
        UpdateData(db


if __name__ == '__main__':
    print