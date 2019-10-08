#!/usr/bin/env python3
import statistics
import math
from heapq import heappush, heappop
import statistics
import ipaddress
import random
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
#-------------------------------------------------
#Define Packet class
class Packet:
    def __init__(self):
        self.SrcIP      = None # 5 tuple - SrcIP
        self.DstIP      = None # 5 tuple - DstIP
        self.Priority   = None 
        self.SrcPort    = None # 5 tuple - SrcPort
        self.DstPort    = None # 5 tuple - DstPort
        self.Protocol   = None # 5 tuple - Protocol
        self.event_type = "Arrival"

#Define TCAM Structure
class Switch_TCAM:
    def __init__(self):
        self.flow_id              = None
        self.first_timestamp      = None
        self.last_timestamp       = None
        self.idle_timeout         = None
        self.packet_count         = None
        self.duration             = None

#init. switch data structure asa dictionary
switch = {}

#Define Data base structure of CP
class Db_content:
    def __init__(self):
            self.timestamp    = list()
            self.idle_timeout = list()
            self.interval     = list() 
            self.active_flag  = None
# DB in CP init. as dict
db = {} 
#-------------------------------------------------
#Event Class
#-------------------------------------------------
class Event():
    def __init__(self, __type):
        self.type = __type
    def __str__(self):
        print(self.type)

class Session():
    def __init__(self, srcIP=None, dstIP=None, priority=None, srcPort=None, dstPort=None, protocol=None):
        super().__init__('Session')
        self.srcIP    = srcIP
        self.dstIP    = dstIP
        self.priority = priority
        self.srcPort  = srcPort
        self.dstPort  = dstPort
        self.protocol = protocol

class Arrival(Event):
    def __init__(self, session_or_arrival):
        assert isinstance(session_or_arrival, Session) or isinstance(session_or_arrival, Arrival) #check if input(session or arrival is Session or Arrival)
        self.srcIP      = session_or_arrival.srcIP
        self.dstIP      = session_or_arrival.dstIP
        self.priority   = session_or_arrival.priority
        self.srcPort    = session_or_arrival.srcPort
        self.dstPort    = session_or_arrival.dstPort
        self.protocol   = session_or_arrival.protocol

class Install(Event):
    def __init__(self):
        super().__init__('Install')
        #found Event == Install, Do sth here?

class Expire(Event):
    def __init__(self):
        super().__init__('Expire')
        #found Event == Expire, Do sth here?

class Monitor(Event): #schedule itself per second
    def __init__(self):
        super().__init__('Monitor')

#------------------------------------------------
#       Places to Declare Variable              #
#------------------------------------------------
db_threshold = 5000       #set maximum # of db size as 5000, but why?
packet_out   = 0          #counter for packet-out on CP 
tcam_max     = 2000       #set upper bound of tcam size
tcam_current = 0          #current tcam status
current_time = 0          #current clock
sim_time     = 30*60      #Total simnulation time
timeline = []             #schedule queue
default_idle_timeout = 7  #init idle_timeout for new flow_entry
confident_range = 0.9     #confident area of chebyshev's 
#-----------------------------------------------#
#                                               #
#                 Part 1 & 2                    #
#                     CP                        #
#-----------------------------------------------#

#generate ipv4 addr. in 140.116.0.0/16
def generate_ipv4():
    bits     = random.getrandbits(32)       # generates an integer with 32 random bits
    addr     = ipaddress.IPv4Address(bits)  # instances an Ipv4 addr from those bits
    addr_str = str(addr)                    # convert it to str
    subnet   = ['140','116']
    subnet.extend(addr_str.split('.')[2:])
    addr_str = str('.'.join(subnet))

    return addr_str


#get flow-id from packet
def packet_processing(Packet):
    #get packet detail as flow_id --> SrcIP + DstIP --> HASH
    flow_id = (packet.SrcIP, packet.DstIP, packet.SrcPort, packet.DstPort, packet.Priority, packet.event_type)
    #Set SrcIP, DstIP, SrcPort, DstPort, Priority, Event_type as flow_id
    packet_out = packet_out + 1
    return flow_id
    
#get flow_id which needs to be removed & delete from db
def lru(db, time):
    #Sorting according to last_timestamp
    #Delete least recently use record from db
    #return db after deletion
    flow_id = sorted(db,lambda x:db[x].timestamp[-1])[0] # get flow_id
    #--------------------------------------------------------------------------------------
    print("Flow_id to delete: ", flow_id," idle for: ", (time - db[flow_id].timestamp[-1]))
    #For Debugging use
    #--------------------------------------------------------------------------------------
    del db[flow_id]
    #return db

#Checking DB size > threshold? do lru if so, till it meet the requirement of threshold
def checkDB(db):
    if(len(db) > db_threshold):
        lru(db)
        checkDB(db)
        
        #check db space till it meets the requirement
        print("Checking DB Size...")
    print("Size suffcient")

            
#Flow entry in cp's DB ?
def checkFlowExist_DB(flow_id, db, time): 
    #To check if DB has this flow record
    if(flow_id in db): #if exist
        db[flow_id].timestamp.append(time)#update current_time as timestamp
        #----------------------------------------------------------------
        print("Flow found in DB, time updated")
        #For debugging use
        #----------------------------------------------------------------
        #determin if this flow is frquent,if so install flow_entry
        checkInterval(db,flow_id,db,current_time)
        #return db
    else:
        #Add record to DB
        db[flow_id] = db_content() #flow_id as key, db_content as value
        db[flow_id].timestamp.append(time) #add new time data
        db[flow_id].idle_timeout = default_idle_timeout#update idle timeout for the first time
        
        #cancel installation & handle packet by cp & update packet out counter
        #return db

#when flow_entry removal occured, updating time stamp & new idle_timeout
def updateData(db, flow_id, idle_timeout = default_idle_timeout, time):
    db[flow_id].idle_timeout.append(idle_timeout)  #if idle_timeout does not receive, append 7 as idle timeout
    db[flow_id].timestamp.append(time)      #update last time stamp

#checking interval for identifying small flow
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
        # switch[flow_id].timestamp    = time
        # switch[flow_id].packet_count = 0 #init as 0
        # switch[flow_id].duration     = None #init as None
        # switch[flow_id].idle_timeout = db[flow_id].idle_timeout[-1]#set idle_timeout from db[flow_id].idle_timeout[-1]
        #Error here，how to indicate new timeout value is available? (using last timeout till new timeout have calculated?)
        install_Rule(flow_id, switch)
        db[flow_id].active_flag      = True


    else:
        print("Cancel installaion of : ", flow_id) #Print the flow id since cancalation

def deleteFlowEntry(tcam, tcam_current): # it seems is the same as LRU function
    #find least used rule in tcam 
    #sort with timestamp, get flow_id
    target = sorted(tcam,lambda x:tcam[x].timestamp[-1])[0]
    #----------------------------------------------
    print("flow to delete in tcam: ",target)
    #----------------------------------------------
    del tcam[target]
    tcam_current = len(tcam)
    return tcam_current, tcam

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
        #get new idle timeout through chebyshev
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
def install_Rule(flow_id, switch):
    switch[flow_id]                   = Switch_TCAM()
    switch[flow_id].first_timestamp   = time
    switch[flow_id].last_timestamp    = time
    switch[flow_id].packet_count      = 0  # init as 0
    switch[flow_id].duration          = None # init as -1

def checkFlowExist_SW(switch, flow_id, time):
    #do sth here
    if(flow_id in switch):
        switch[flow_id].packet_count   = switch[flow_id].packet_count + 1
        switch[flow_id].last_timestamp = time
        switch[flow_id].duration       = time - switch[flow_id].last_timestamp
        return True
    else:
        #install_Rule(flow_id, switch)
        #call install rule @ other side
        return False

#class Switch_TCAM:
#    def __init__(self):
#       self.timestamp      = list()
#       self.packet_count   = None
#       self.duration       = None


    
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


''' 
def next_session(priority = 1):
    s = Session()
    s.srcIP     = generate_ipv4()
    s.dstIP     = generate_ipv4()
    s.srcPort   = 1111
    s.dstPort   = 1111
    s.protocol  = 0x800
'''

#--------------------------------------------------------------------
###########---Simulation starts here---###########


##init event
event_a = Arrival()
heappush(timeline, (0 + np.random.exponential(1), event_a))


while(current_time < sim_time):
    #get data from timeline queue
    ts , p = heappop(timeline)

    #update  current time
    current_time = ts

    #Do sth
    #Check DB Size
    CheckDB(db)

    #update event
    if p.event_type == "Arrival":
        #schedule next arrival event
        heappush(timeline, (ts + np.random.exponential(1),p)) #对应obj(schedule new arrival))
        #check is flow_entry timeout-->what if flow_entry not exists?
        if(checkFlowExist_SW(switch,flow_id,current_time)):
            #if switch has corresponding flow entry,just update statistics.
            if(current_time - db[p.flow_id].timestamp[-1] < switch[p.flow_id].idle_timeout):#means not timeout, schdule new expire event
                heappush(timeline, #下次expire时间, #对应obj)
            else:
                #packet-in to controller
                checkFlowExist_DB(flow_id, db,current_time)
        #update flow_id 
        flow_id = PacketProcessing(p) #p stands for packet object
        
        
        #check if exist in db & update timestamp & maintain packet-out counter @ controller
        db = CheckFlowExist_DB(flow_id,db)
        #am I supposed to schdule an install event here? or just execute install event?

    if p.event_type == "Install":
        flow_id = PacketProcessing(p)
        #check interval & determin installation vaild
        checkInterval(db,flow_id,switch,current_time)





    if p.event_type == "Monitor":
        heappush(timeline, (ts + 1, #对应obj)
        #記錄tcam狀態
    if p.event_type == "expire":
        flow_id = packet_processing
        processingRemovalMessage(db, flow_id,duration,packet_count,current_time)
        db,TCAM_Current = Del_Rule(db,TCAM_Max)
    
