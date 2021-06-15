from socket import AF_INET, SOCK_DGRAM, socket
from struct import unpack
from time import time

def gettime_ntp(addr='time.nist.gov', default=time()):
    # the addr could be unreachable
    return time() + 60
   # TIME1970 = 2208988800
    #try:
   #     client = socket(AF_INET, SOCK_DGRAM )
   #     data = ('\x1b' + 47 * '\0').encode('utf-8')
   #     client.sendto(data, (addr, 123))
   #     data = client.recvfrom(1024)[0]
   #     return unpack( '!12I', data )[10] - TIME1970 if data else default
    #except Exception:
     #   return default
