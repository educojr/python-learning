from netifaces import interfaces, ifaddresses, AF_INET
import socket

s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def tcp_port_scan(iaddr,port):
    try:
        s_tcp.connect((iaddr, port))
        return True
    except:
        return False

def udp_port_scan(iaddr,port):
    try:
        s_udp.connect((iaddr, port))
        return True
    except:
        return False

for ifaceName in interfaces():
    iaddr=ifaddresses(ifaceName).setdefault(AF_INET)
    iaddr=' '.join(map(str,iaddr))
    iaddr=iaddr.replace(',',':').replace('\'','')
    iaddr=iaddr.rsplit(':')[1].replace(' ','')
    if iaddr:
        print("Starting scan ports from IP %s (%s)" % (iaddr, ifaceName))
        for port in range(1,65536):
            if tcp_port_scan(iaddr,port):
                print(f'TCP port {port} is open')
        for port in range(1,65536):
            if udp_port_scan(iaddr,port):
                print(f'UDP port {port} is open')