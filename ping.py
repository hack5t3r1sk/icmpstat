#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### TODO: handle this error:
# ..|Exception in thread Thread-16905:
# Traceback (most recent call last):
#   File "/usr/lib/python3.5/threading.py", line 914, in _bootstrap_inner
#     self.run()
#   File "/usr/lib/python3.5/threading.py", line 862, in run
#     self._target(*self._args, **self._kwargs)
#   File "/app/ping.py", line 52, in send
#     reply = sr(IP(dst=self.hostIp)/ICMP(), timeout=self.timeout)
#   File "/usr/local/lib/python3.5/dist-packages/scapy/sendrecv.py", line 377, in sr
#     s.close()
#   File "/usr/local/lib/python3.5/dist-packages/scapy/arch/linux.py", line 439, in close
#     set_promisc(self.ins, i, 0)
#   File "/usr/local/lib/python3.5/dist-packages/scapy/arch/linux.py", line 168, in set_promisc
#     mreq = struct.pack("IHH8s", get_if_index(iff), PACKET_MR_PROMISC, 0, b"")
#   File "/usr/local/lib/python3.5/dist-packages/scapy/arch/linux.py", line 375, in get_if_index
#     return int(struct.unpack("I",get_if(iff, SIOCGIFINDEX)[16:20])[0])
#   File "/usr/local/lib/python3.5/dist-packages/scapy/arch/common.py", line 24, in get_if
#     ifreq = ioctl(sck, cmd, struct.pack("16s16x", iff.encode("utf8")))
# OSError: [Errno 19] No such device
# 

class ScapyNotFound(Exception):
    """Exception in case Scapy is not found"""
    def __init__(self, msg=None):
        if msg is None:
            msg = '\n*** ERROR: something wrong happened while importing scapy.\n'
        super(ScapyNotFound, self).__init__(msg)




import json,logging,time

# Supress warnings at import
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

# Import scapy
try:
    from scapy.all import *
except ImportError:
    #raise ScapyNotFound
    raise ScapyNotFound(msg='\n*** ERROR: could not import Scapy. Please install it and try again ("pip3 install scapy").\n')

# conf is imported from scapy
conf.verb=0


class Ping():
    def __init__(self, host, timeout=15, cycleId=None, debug=False):
        # Set props from args
        self.hostIp, self.hostAlias = host
        self.timeout = timeout
        self.cycleId = cycleId
        self.debug = debug
        self.shouldStop = False
        self.answered = []
        self.unanswered = False
        self.startTime = None
        self.endTime = None
        self.time = None
        
    def send(self):
        # if we're not canceled at this point, go
        if not self.shouldStop:
            # Remember start-time
            self.startTime = time.time()
            
            # Ping the peer
            reply = sr(IP(dst=self.hostIp)/ICMP(), timeout=self.timeout)
            if not (reply is None):
                self.answered, self.unanswered = reply
            else:
                self.answered   = False
                self.unanswered = True
            if self.debug and not self.answered and self.unanswered:
                print('\n### DEBUG ### ===> [%s] (%s) : NO ANSWER !' % (self.hostAlias,self.hostIp))
            
            # Remember end-time
            self.endTime = time.time()
            self.time    = round(self.endTime - self.startTime, 3)
            self.stop()

    def stop(self):
        if self.debug and self.startTime is None:
            print('\n### DEBUG ### ===> [%s] (%s) : STOPPED BEFORE BEING STARTED !' % (self.hostAlias,
                                                                                       self.hostIp,
                                                                                       self.startT
                                                                                      ))
        self.shouldStop = True

    def status(self):
        if not self.shouldStop:
            return 'ACTIVE'
        else:
            if self.startTime is None:
                return 'NEVER STARTED'
            else:
                return 'DONE (answered)' if self.answered else 'DONE (UNANSWERED)'
    
    def toDict(self):
            return {
                    'cycleId': self.cycleId,
                    'hostIp': self.hostIp,
                    'hostAlias': self.hostAlias,
                    'answered': True if len(self.answered) else False, 
                    'unanswered': True if len(self.unanswered) else False,
                    'status': self.status(),
                    'startTime': self.startTime,
                    'endTime': self.endTime,
                    'time': '%.3f' % self.time,
                    'timeout': self.timeout
                    }
