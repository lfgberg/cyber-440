# PCAP Parsing

I'm provided with a PCAP full of only headers, no application data. It's huge.

## Method

1. I ran BruteShark on the dataset to get a network diagram and a JSON of open ports
2. Diagram was too cluttered and the open ports included ephemeral ports
3. Created a python script to parse the JSON and build a list of open ports excluding ephemeral ports
   1. Add src/dst host to dict if not present
   2. if destport is not ephemeral and is not present, add to dict
   3. json dump dict
