#!/usr/bin/env python3
import statistics
import math
from heapq import heappush, heappop
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
class Packet:
    def __init__(self):
        self.SrcIP      = None # 5 tuple - SrcIP
        self.DstIP      = None # 5 tuple - DstIP
        self.Priority   = None 
        self.SrcPort    = None # 5 tuple - SrcPort
        self.DstPort    = None # 5 tuple - DstPort
        self.Protocol   = None # 5 tuple - Protocol
        self.event_type = "arrival"


class Switch_TCAM:
    def __init__(self):
        self.flow_id        = None
        self.first_timestamp      = None
        self.last_timestamp      = None
        self.idle_timeout   = None
        self.packet_count   = None
        self.duration       = None

switch = {}


class Db_content:
    def __init__(self):
            self.timestamp    = list()
            self.idle_timeout = list()
            self.interval     = list() 
            self.active_flag  = None

db = {} # db init as dict

#------------------------------------------------
#       Places to Declare Variable              #
#------------------------------------------------
db_threshold = 5000   #set maximum # of db size as 5000
packet_out   = 0      #maintain system load counter
tcam_max     = 2000   #set upper bound of tcam size
tcam_current = 0      #current tcam status
current_time = 0
sim_time     = 30*60  #simnulation time
timeline = []         #queue for schedule
default_idle_timeout = 7
confident_range = 0.9
#-----------------------------------------------#
#                                               #
#                 Part 1 & 2                    #
#                     CP                        #
#-----------------------------------------------#
def packet_processing(Packet):
    #get packet detail as flow_id --> SrcIP + DstIP --> HASH
    flow_id = (packet.SrcIP, packet.DstIP, packet.SrcPort, packet.DstPort, packet.Priority, packet.event_type)
    #Set SrcIP, DstIP, SrcPort, DstPort, Priority, Event_type as flow_id
    return flow_id
    

def lru(db,time):
    #Sorting according to last_timestamp
    #Delete least recently use record from db
    #return db after deletion
    flow_id = sorted(db,lambda x:db[x].timestamp[-1])[0] # get flow_id
    print("Flow_id to delete: ", flow_id," idle for: ", (time - db[flow_id].timestamp[-1]))
    del db[flow_id]
    #return db


def checkDB(db):
    #DB size > threshold?
    if(len(db) > db_threshold):
        lru(db)
        checkDB(db)
        
        #check db space till it meets the requirement
        print("Checking DB Size...")

            

def checkFlowExist_DB(flow_id, db, time): #Flow entry in DB ?
    #To check if DB has this flow record
    if(flow_id in db): #if exist
        db[flow_id].timestamp.append(time)#update timestamp
        print("Flow found in DB, time updated")
        #return db
    else:
        #Add record to DB
        db[flow_id] = db_content() #flow_id as key, db_content as value
        db[flow_id].timestamp.append(time) #add new time data
        db[flow_id].idle_timeout = default_idle_timeout#update idle timeout for the first time
        packet_out = packet_out + 1
        #cancel installation & handle packet by cp & update packet out counter
        #return db


def updateData(db, flow_id, idle_timeout = 7.0, time): #when removal occur,updating time stamp & idle_timeout
    db[flow_id].idle_timeout.append(idle_timeout)  #if idle_timeout does not receive, append 7 as idle timeout
    db[flow_id].timestamp.append(time)      #update last time stamp

def checkInterval(db, flow_id, switch, time):
    tmp = db[flow_id].timestamp[len(db[flow_id].timestamp) - 1] #get last time stamp
    print("Checking Interval : ", tmp)
    
    if(time - tmp < 11): 
        #meet the requirement of interval & proceed to install 
        while(tcam_current >= tcam_max - 1 ):
            #if tcam gets full after installation, execute delete process
            tcam_current = deleteFlowEntry(db, tcam_current)
            #Keep checking row 121-126 to make sure tcam size sufficient
        #out of while loop, tcam space is suffcient, execute install process
        tcam_current = tcam_current + 1
        switch[flow_id].timestamp    = time
        switch[flow_id].packet_count = 0 #init as 0
        switch[flow_id].duration     = None #init as None
        switch[flow_id].idle_timeout = db[flow_id].idle_timeout[-1]#set idle_timeout from db[flow_id].idle_timeout[-1]
        db[flow_id].active_flag      = True

        # if(TCAM_Current < TCAM_Max):
        #     #install
        #     TCAM_Current = TCAM_Current + 1 
        #     #更新TCAM用量
        #     #db[flow_id].interval.clear()
        #     #意义不明，interval不就是用来帮助确定是否插入 & 决定idle_timeout吗？为什么要clear
        #     #Clear interval list
        #     db[flow_id].active_flag = True
        #     #在DB中對已插入的flow做標記
        # else:
        #     #進行Flow Mod
        #     DeleteFlowEntry(db, TCAM_Current)
            

    else:
        print("Cancel installaion of : ", flow_id) #Print the flow id since cancalation

def deleteFlowEntry(db, tcam_current): # it seems is the same as LRU function
    #找到DB中有active flag之最不常用的flow
    #需要根據timestamp排序，剔除最後的記錄
    #找到要删除的条目
    target = sorted(db,lambda x:db[x].timestamp[-1])[0]
    del db[target]
    tcam_current = len(db)
    return tcam_current, db

def processingRemovalMessage(db, flow_id, duration, packet_count, time):
    #update time stamp
    db[flow_id].timestamp.append(time)
    #mark flow as inactive
    db[flow_id].active_flag = False
    #free tcam spaces
    tcam_current = tcam_current - 1 
    #Calculate time interval based last two timestamp
    interval = db[flow_id].timestamp[len(db[flow_id].timestamp) - 1] - db[flow_id].timestamp[len(db[flow_id].timestamp) - 2]
    #update interval
    db[flow_id].interval.append(interval)

    #check if len(interval) >= 6 --->Threshold 3
    if(len(db[flow_id].interval) >= 6):
        #calculate mean through interval list
        mean     = statistics.mean(db[flow_id].interval)
        #Calculate variance through interval list
        vairance = statistics.variance(db[flow_id].interval)
        stdev    = statistics.stdev(db[flow_id].interval)
        #get new idle timeout through 柴比雪夫
        new_timeout = chebyshev(mean, stdev)
        #update data to db
        db[flow_id].interval.clear()
        #Clear interval list
        updateData(db, flow_id, new_timeout)

def chebyshev(mean, stdev, db, confident_range):
    k = math.sqrt(1/1-confident_range)
    result = mean + (k * stdev)
    return result


def removalMessage(flow_id, switch):
    return switch[flow_id].duration, Switch[flow_id].packet_count

#------------------------------------------------
#                                               #
#                   Part 3                      #
#                   Switch                      #
#------------------------------------------------
def checkFlowExist_SW(switch, flow_id, time):
    #do sth here
    if(flow_id in switch):
        switch[flow_id].packet_count   = switch[flow_id].packet_count + 1
        switch[flow_id].last_timestamp = time
        switch[flow_id].duration       = time - switch[flow_id].last_timestamp
    else:
        install_Rule(flow_id, switch)

#class Switch_TCAM:
#    def __init__(self):
#       self.timestamp      = list()
#       self.packet_count   = None
#       self.duration       = None

def install_Rule(flow_id, switch):
    switch[flow_id]                   = Switch_TCAM()
    switch[flow_id].first_timestamp   = time
    switch[flow_id].last_timestamp    = time
    switch[flow_id].packet_count      = 0  # init as 0
    switch[flow_id].duration          = None # init as -1
    
def del_Rule(switch, tcam_max):
    tcam_current = len(switch)
    
    if(tcam_current >= tcam_max):
        # TCAM Overflow occur
        switch = lru(Switch)
        tcam_current = len(switch)
        #sorted by timestamps & find flow id to delete
        
        #不用接，直接对字典进行操作
    
        return switch, tcam_current

    else:

        return switch, tcam_current
#---------------------------------------------------------------------
# TCAM_Current = len(Switch)
# while(TCAM_current >= TCAM_Max):
#     Switch,TCAM_Current = Del_Rule(Switch, TCAM_Max)
#---------------------------------------------------------------------




if __name__ == '__main__':

#init


##arrival event
packet_arrival = packet()
Src_ip, Dst_ip = random.sample(IP_List,2) #从list中抓两个ip出来
Port           = random.sample(Port_list,1) #从list中抓port出来，list期望存常用port
Protocol       = random.sample(Protocol_list,1)
Priority       = random.sample(Priority_list,1)

packet_arrival.SrcIP      = Src_ip
packet_arrival.DstIP      = Dst_ip
packet_arrival.SrcPort    = Port
packet_arrival.DstPort    = Port
packet_arrival.Priority   = Priority
packet_arrival.Protocol   = Protocol
packet_arrival.event_type = "arrival"

##install event ---> schedule expire event
packet_install              = Switch_TCAM()
packet_install.flow_id      = (packet_arrival.SrcIP, packet_arrival.DstIP, packet_arrival.SrcPort, packet_arrival.DstPort, packet_arrival.Protocol, packet_arrival.Priority)
#store as tuple
packet_install.idle_timeout = db[packet_install.flow_id].idle_timeout[-1]
packet_install.packet_count = 0
packet_install.timestamp    = time.time()
packet_install.duration     = db[flow_id].timestamp[-1] - db[flow_id].timestamp[-2] #calculating time stamp 有疑惑
packet_install.event_type   = "install"

##expire event ---> schedule for nothing
packet_expire               = Switch_TCAM()

packet_expire.flow_id       = packet_install.flow_id
packet_expire.duration      = Switch[packet_expire.flow_id].duration
packet_expire.idle_timeout  = Switch[packet_expire.flow_id].idle_timeout
packet_expire.packet_count  = Switch[packet_expire.flow_id].packet_count
packet_expire.timestamp #it seems unnecessary


while(Current_time < Sim_time):
    #get data from timeline queue
    ts , p = heappop(timeline)

    #update  current time
    Current_time = ts

    #Do sth
    #Check DB Size
    CheckDB(db)

    #update event
    if p.event_type == "arrvial":
        
        heappush(timeline, (ts + np.random.exponential(1), #对应obj(schedule new arrvial))
        #schedule next event
        flow_id = PacketProcessing(p)
        #update flow_id 
        db = CheckFlowExist_DB(flow_id,db)
        #check if exist in db & update timestamp & maintain packet-out counter @ controller




    if p.event_type == "install":
        heappush(timeline, (ts + np.random.exponential(1), #对应obj)
    if p.event_type == "expire":
        if(time.time() - db[p.flow_id].timestamp[-1] < db[p.flow_id].idle_timeout):
            heappush(timeline, #下次expire时间, #对应obj)
        else:
            db,TCAM_Current = Del_Rule(db,TCAM_Max)
    
