import xml.etree.ElementTree as ET

def main():
    # Define the XML namespace
    namespace = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}

    # Path to your XML file containing EVTX records
    path = "SecurityLog-rev2.xml"

    # Parse XML
    XMLData = readXML(path)

    # Read events + get data
    events = parseData(XMLData, namespace)

    #for event in events:
    #    print(event)

    # Print the data we need
    print("Part A:")
    print(f'First event time: {events[0]['TimeCreated']}')
    print(f'Last event time: {events[len(events) - 1]['TimeCreated']}')
    print(f'Event count: {len(events)}')

    exit()

def parseData(XMLData, namespace):
    root = XMLData

    events = []

    # Iterate over each event
    for event in root.findall("ns:Event", namespace):
        # Extract various data from the event (e.g., EventID, TimeCreated)
        event_id = event.find("ns:System/ns:EventID", namespace).text
        time_created = event.find("ns:System/ns:TimeCreated", namespace).attrib.get('SystemTime')

        # You can extract more fields as needed here
        # Example: Extract event provider name
        provider_name = event.find("ns:System/ns:Provider", namespace).attrib.get('Name')
    
        # Store the data in a dictionary
        event_data = {
            'EventID': event_id,
            'TimeCreated': time_created,
            'ProviderName': provider_name
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