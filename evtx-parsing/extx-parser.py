import xml.etree.ElementTree as ET
from datetime import datetime

def main():
    # Define the XML namespace
    namespace = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}

    # Path to your XML file containing EVTX records
    path = "SecurityLog-rev2.xml"

    # Parse XML
    XMLData = readXML(path)

    # Read events + get data
    events = parseData(XMLData, namespace)
    logons = tallyLogons(events)
    uniqueLogins = tallyUniqueLogons(logons)
    eventCounts = countLogonEvents(events)

    # Print the data we need
    print("----- Stage 1 -----")
    print("----- Part A -----")
    print(f'First event time: {events[0]['TimeCreated']}')
    print(f'Last event time: {events[len(events) - 1]['TimeCreated']}')
    print(f'Event count: {len(events)}')

    print("----- Part B -----")
    print(f'Logon event count: {eventCounts[0]}')
    print(f'Unique user logins: {uniqueLogins}')
    print("Report generated with logins per user.")
    print(logons)

    print("----- Part C -----")
    print(f'Logon event count: {eventCounts[1]}')

    print("----- Stage 2 -----")
    print("Report generated with logins and failed logins over time.")

    exit()

def groupByHour(events):
    report = {
        '4625',
        '4624'
    }

    for event in events:
        # Format the time
        time = event['TimeCreated']
        time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
        hour = time.strftime('%Y-%m-%dT%H')

        if (event['EventID'] == "4624"):
            report['4624'][]

def tallyUniqueLogons(logons):
    uniqueUsers = set()  # Use a set to automatically handle uniqueness

    # Iterate over the logons per user
    for user in logons.keys():
        # Exclude computer accounts that end with '$'
        if not user.endswith('$'):
            uniqueUsers.add(user)

    return len(uniqueUsers)

def tallyLogons(events):
    logons = {}

    for event in events:
        if event['EventID'] == '4624':
            username = event['TargetUserName']

            if username in logons:
                logons[username] += 1
            else:
                logons[username] = 1
    
    return logons

def countLogonEvents(events):
    logonCount = 0
    logoffCount = 0

    for event in events:
        if event['EventID'] == '4624':
            logonCount += 1
        else:
            logoffCount += 1
    
    return [logonCount, logoffCount]

def parseData(XMLData, namespace):
    root = XMLData

    events = []

    # Iterate over each event
    for event in root.findall("ns:Event", namespace):
        # Filter down to logon/failed logon events
        eventId = event.find("ns:System/ns:EventID", namespace).text

        if (eventId != "4624" and eventId != "4625"):
            continue

        # Extract various data from the event (e.g., EventID, TimeCreated)
        timeCreated = event.find("ns:System/ns:TimeCreated", namespace).attrib.get('SystemTime')
        
        # Extract TargetUserName and TargetComputer from EventData
        event_data_section = event.find("ns:EventData", namespace)
        targetUser = None
        targetComputer = None

        for data in event_data_section.findall("ns:Data", namespace):
            if data.attrib.get('Name') == "TargetUserName":
                targetUser = data.text
            elif data.attrib.get('Name') == "TargetDomainName":
                targetComputer = data.text

        # You can extract more fields as needed here
        # Example: Extract event provider name
        providerName = event.find("ns:System/ns:Provider", namespace).attrib.get('Name')
    
        # Store the data in a dictionary
        event_data = {
            'EventID': eventId,
            'TimeCreated': timeCreated,
            'ProviderName': providerName,
            'TargetComputer': targetComputer,
            'TargetUserName': targetUser
        }

        # Append the event data to the list
        events.append(event_data)

    return events

def readXML(path):
    # Parse the XML file
    tree = ET.parse(path)
    root = tree.getroot()

    return root

if __name__=="__main__":
    main()