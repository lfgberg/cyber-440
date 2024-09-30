import json

def main():

    # Load the JSON file
    data = readJson('network-map.json')

    # Parse the data
    results = parseData(data)

    # Save the results
    saveResults(results, 'results.txt')
    
    exit()

class Host(object):
    def __init__(self, ip):
        self.ip = ip

        self.tcpSent = []
        self.tcpRecieved = []
        self.tcpOpen = []

        self.udpSent = []
        self.udpRecieved = []
        self.udpOpen = []
    
    def __eq__(self, other):
        return isinstance(other, Host) and self.ip == other.ip

    # TCP

    # If we haven't seen the port before add to sent, if it's been sent and recieved then it's open
    def addTcpSendPort(self, port):
         if port not in self.tcpSent:
            self.tcpSent.append(port)
            if (port in self.tcpRecieved) and (port not in self.tcpOpen): 
                self.tcpOpen.append(port)
            elif int(port) <= 1023 and (port not in self.tcpOpen):
                self.tcpOpen.append(port)

    # If we haven't seen the port before add to recieved, if it's well known add to open
    def addTcpRecievedPort(self, port):
        if port not in self.tcpRecieved:
            self.tcpRecieved.append(port)

    # UDP

    # If we haven't seen the port before add to sent, if it's been sent and recieved then it's open
    def addUdpSendPort(self, port):
        if port not in self.udpSent:
            self.udpSent.append(port)
            if (port in self.udpRecieved) and (port not in self.udpOpen): 
                self.udpOpen.append(port)
            elif int(port) <= 1023 and (port not in self.udpOpen):
                self.udpOpen.append(port)

    # If we haven't seen the port before add to recieved, if it's well known add to open
    def addUdpRecievedPort(self, port):
        if port not in self.udpRecieved:
            self.udpRecieved.append(port)


def saveResults(results, fileName):
    with open(fileName, 'w') as outfile:
        for ip, host in results.items():
            # Check if there are any open TCP or UDP ports
            if host.tcpOpen or host.udpOpen:
                outfile.write(f"IP: {ip}\n")
                
                # Print open TCP ports
                if host.tcpOpen:
                    outfile.write(f"  Open TCP Ports: {', '.join(map(str, host.tcpOpen))}\n")
                
                # Print open UDP ports
                if host.udpOpen:
                    outfile.write(f"  Open UDP Ports: {', '.join(map(str, host.udpOpen))}\n")

                outfile.write("\n")

def parseData(data):
    results = {}

    for entry in data:
        srcIp = entry['Source']
        destIp = entry['Destination']
        protocol = entry['Protocol']
        srcPort = entry['SrcPort']
        destPort = entry['DestPort']

        # Create new hosts in results if needed
        if srcIp not in results:
            results[srcIp] = Host(srcIp)
        if destIp not in results:
            results[destIp] = Host(destIp)

        if (protocol == "TCP"):
            results[srcIp].addTcpSendPort(srcPort)
            results[destIp].addTcpRecievedPort(destPort)
        else:
            results[srcIp].addUdpSendPort(srcPort)
            results[destIp].addUdpRecievedPort(destPort)
    
    return results

def readJson(filePath):
    # Load the JSON file
    with open(filePath, 'r') as file:
        data = json.load(file)
    
    # Return the data
    return data

if __name__=="__main__":
    main()