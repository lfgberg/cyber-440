import xml.etree.ElementTree as ET
from datetime import datetime
import matplotlib.pyplot as plt
import json

def main():
    # Define the XML namespace
    namespace = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}

    # Path to your XML file containing EVTX records
    path = "events.xml"

    # Parse XML
    XMLData = readXML(path)

    # Read events + get data
    events = parseData(XMLData, namespace)
    logonEvents = parseLogonData(XMLData, namespace)
    logons = tallyLogons(logonEvents)
    uniqueLogins = tallyUniqueLogons(logons)
    eventCounts = countLogonEvents(logonEvents)
    loginReport = groupByHour(logonEvents, "4624")
    failedLoginReport = groupByHour(logonEvents, "4625")

    # User login reports
    mattEdwardsReport = groupUserLogonByHour(logonEvents, 'Matt.Edwards')
    grantLarsonReport = groupUserLogonByHour(logonEvents, 'grant.larson')
    plotFrequencyChart(mattEdwardsReport, "Matt Edwards")
    plotFrequencyChart(grantLarsonReport, "Grant Larson")

    # Get times
    sortedEvents = sorted(events, key=lambda x: datetime.strptime(x['TimeCreated'], "%Y-%m-%dT%H:%M:%S.%fZ"))

    # Save reports
    #saveReport(logons, 'logon-by-users-report.json')
    #saveReport(loginReport, 'logon-by-hour-report.json')
    #saveReport(failedLoginReport, 'failed-login-by-hour-report.json')

    # Print the data we need
    print("----- Stage 1 -----")
    print("----- Part A -----")
    print(f'First event time: {sortedEvents[0]['TimeCreated']}')
    print(f'Last event time: {sortedEvents[len(sortedEvents) - 1]['TimeCreated']}')
    print(f'Event count: {len(events)}')

    print("----- Part B -----")
    print(f'Logon event count: {eventCounts[0]}')
    print(f'Unique user logins: {uniqueLogins}')
    print("Report generated with logins per user.")

    print("----- Part C -----")
    print(f'Logon event count: {eventCounts[1]}')

    print("----- Stage 2 -----")
    print("Report generated with logins and failed logins over time.")
    print("Login frequency charts generated for matt.edwards and grant.larson.")

    exit()

def saveReport(report, filename):
    with open(filename, 'w') as file:
        json.dump(report, file, indent=4)

def plotFrequencyChart(report, username):
    # Generate plot
    sortedReport = dict(sorted(report.items()))
    plt.bar(sortedReport.keys(), sortedReport.values())

    # Format the plot
    plt.xlabel('Hour')
    plt.ylabel('Login Count')
    plt.title(f'{username} Login Frequency')
    plt.xticks(rotation=45, ha='right')

    # Show the plot
    plt.tight_layout()
    plt.savefig(f'{username}-login-chart.png', format='png', dpi=300)
    plt.clf()

def groupUserLogonByHour(events, username):
    report = {}

    for event in events:
        if (event['EventID'] != '4624'):
            continue

        if (event['TargetUserName'] != username):
            continue

        # Format the time
        time = event['TimeCreated']

        if isinstance(time, str):
                # Truncate any extra fractional seconds and parse
                if '.' in time:
                    main_time, fraction = time.split('.')
                    fraction = fraction[:6]  # Truncate to 6 digits (microseconds)
                    time = f"{main_time}.{fraction}Z"

        time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')

        hour = time.strftime('%Y-%m-%dT%H')
    
        if (hour in report):
            report[hour] += 1
        else:
            report[hour] = 1
    
    return report

def groupByHour(events, id):
    report = {}

    for event in events:
        if (event['EventID'] != id):
            continue

        # Format the time
        time = event['TimeCreated']

        if isinstance(time, str):
                # Truncate any extra fractional seconds and parse
                if '.' in time:
                    main_time, fraction = time.split('.')
                    fraction = fraction[:6]  # Truncate to 6 digits (microseconds)
                    time = f"{main_time}.{fraction}Z"

        time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')

        hour = time.strftime('%Y-%m-%dT%H')
    
        if (hour in report):
            report[hour] += 1
        else:
            report[hour] = 1
    
    return report

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
        # Extract various data from the event (e.g., EventID, TimeCreated)
        timeCreated = event.find("ns:System/ns:TimeCreated", namespace).attrib.get('SystemTime')
        eventId = event.find("ns:System/ns:EventID", namespace).text
    
        # Trim extra digits in the microseconds part if present
        if '.' in timeCreated:
            timeCreated = timeCreated[:timeCreated.index('.') + 7] + 'Z'

        # Store the data in a dictionary
        event_data = {
            'EventID': eventId,
            'TimeCreated': timeCreated,
        }

        # Append the event data to the list
        events.append(event_data)

    return events

def parseLogonData(XMLData, namespace):
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
        providerName = event.find("ns:System/ns:Provider", namespace).attrib.get('Name')
        targetUser = None
        targetComputer = None

        for data in event_data_section.findall("ns:Data", namespace):
            if data.attrib.get('Name') == "TargetUserName":
                targetUser = data.text
            elif data.attrib.get('Name') == "TargetDomainName":
                targetComputer = data.text
    
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