# ICMPStat - ping multiple hosts in parallel

### About me
ICMPStat enables you to ping multiple hosts in parallel in order to generate statistics.

### Statistics
Currently ICMPStat supports:
- exporting your stats to JSON for later processing/visualisation
- generating PNG bar-graphs after each pings-loop for monitoring the results while pinging
- displaying (or not) the statistics to stdout

### Dependencies
##### Required
- system: `python3 python3-pip python3-setuptools python3-wheel`
- pip: `pip3 install scapy`
 
##### Optional
- system: `python3-tk` (for matplotlib to work)
- pip: `pip3 install matplotlib netaddr numpy`

### Usage
```
user@host:~ $ icmpstat -h

  Usage: icmpstat [-Ddhnp] [-i interval] [-s logSuffix] [-S session-ID] [-t timeOut] ip[:alias] [ip[:alias] ...]

OPTIONS:
 -D, --debug            Enable debug-messages
 -h, --help             This help message
 -l, --no-log           Enable logging of the results
 -p, --plot-results     Draw the graphs to PNG files
 -q, --quiet            Disable displaying of the results
 -j, --json             Enables exporting the results to JSON
 
PARAMETERS:
 -t intOrFloat, --timeout=intOrFloat      Define the timeout for the ICMP packets (default=5)
 -t range, --timeout=range                Example: '.5:2.5:1' would do three cycles: 0.5, 1.5 and 2.5
 -c int, --count=int                      Define the count (default=0)
 -i intOrFloat, --interval=intOrFloat     Define the interval between two ICMP packets (default=1)
 -I string, --session-id =string          Use a user-defined session-ID instead of the generated one
 -S string, --log-suffix=string           Use a user-defined suffix instead of the default one ('icmpStat')
 
Example: draw the graphs to PNG files without logging nor displaying the results
icmpstat -pqc 10 -t .1:3.1:1 192.168.1.1:wlan \
                             192.168.178.1:fritz \
                             9.9.9.9:DNS-US \
                             103.199.156.80:DNS-India-Lalkua

The above example would send:
 - 10 pings with timeout 0.1s
 - 10 pings with timeout 1.1s
 - 10 pings with timeout 2.1s
 - 10 pings with timeout 3.1s
to each of the 4 hosts given as arguments.

```

