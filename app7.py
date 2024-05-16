import re
import logging
import sys
import datetime
from ipaddress import ip_network, IPv4Address

logger = logging.getLogger(__name__)

class entryLog:

    def __init__(self, ip, clientID, userID, time, request, statusCode, size, referer, userAgent):
        self.ip = ip
        self.clientID = clientID
        self.userID = userID
        self.time = time
        self.request = request
        self.statusCode = statusCode
        self.size = size
        self.referer = referer
        self.userAgent = userAgent
    
    def __str__(self):
        return f"{self.ip} {self.clientID} {self.userID} {self.time} {self.request} {self.statusCode} {self.size} {self.referer} {self.userAgent}"

def print_total_bytes(log_entries, filter):
    # Regular expression pattern
    regex_pattern = r'([^ ]+)'

    total_size = 0

    for entry in log_entries:
        if entry is not None:
            match = re.match(regex_pattern, entry.request).group(1)
            if match == filter:
                total_size+=entry.size
    
    return total_size

def print_requests_by_browser(log_entries, browser):
    count = 0
    for entry in log_entries:
        if entry is not None and browser in entry.userAgent:
            print(entry)
            
def print_requests_by_ip(log_entries, subnet, lines_per_page):
    count = 0
    for entry in log_entries:
        if entry is not None and ip_in_subnet(entry.ip, subnet):
            print(entry.request.rstrip())
            count += 1
            if count % lines_per_page == 0:
                input("Press Enter to continue...")

def ip_in_subnet(ip, subnet):
    # Check if the IP address belongs to the given subnet.
    network = ip_network(subnet)
    return ip in network

def parse_log_file(log_file):
    # Parsing log file
    log_entries = []
    for log in log_file:
        log_entries.append(parse_log_line(log))
    return log_entries

def parse_log_line(log_line):
    # Regular expression to parse the log line
    log_pattern = re.compile(
        r'(?P<ip>\S+) '
        r'(?P<clientID>\S+) '
        r'(?P<userID>\S+) '
        r'\[(?P<time>[^\]]+)\] '
        r'"(?P<request>[^"]*)" '
        r'(?P<statusCode>\d+) '
        r'(?P<size>\d+|-) '
        r'"(?P<referer>[^"]*)" '
        r'"(?P<userAgent>[^"]*)"'
    )

    # Match the pattern
    match = log_pattern.match(log_line)

    if match:
        # Extracting fields
        ip = IPv4Address(match.group('ip'))
        clientID = match.group('clientID')
        userID = match.group('userID')
        time_str = match.group('time')
        request = match.group('request')
        statusCode = int(match.group('statusCode'))
        size = int(match.group('size')) if match.group('size') != '-' else None
        referer = match.group('referer')
        userAgent = match.group('userAgent')
        
        # Convert time to datetime object
        time_format = '%d/%b/%Y:%H:%M:%S %z'
        time = datetime.datetime.strptime(time_str, time_format)

        # Create entryLog object
        log_entry = entryLog(ip, clientID, userID, time, request, statusCode, size, referer, userAgent)

        return log_entry
    else:
        return None

def read_log_file(log_filename):
    # Check if the log file exists
    try:
        configFile = open('lab.config', 'r')
    except FileNotFoundError:
        print('Log file not found. Exiting application.')
        sys.exit()

    # Read the log file into memory
    try:
        with open(log_filename, 'r') as file:
            log_lines = file.readlines()
    except Exception as e:
        print(f"An error occurred while reading the log file: {e}")
        sys.exit()

    return log_lines

def loadConfig():
    display_settings = {
        "lines": 10,      # Default value for lines
        "separator": ",",   # Default value for separator
        "filter": "ALL"     # Default value for filter
    }
    log_filename = None
    log_level = "WARNING"  # Default log level

    try:
        configFile = open('lab.config', 'r')
    except FileNotFoundError:
        print('No config file found. Exiting application.')
        sys.exit(1)

    # Regular expressions for parsing the config file
    section_re = re.compile(r'\[(.*?)\]')
    param_re = re.compile(r'(\w+)\s*=\s*(.+)')
    
    # Variables to hold the current section being parsed
    current_section = None

    for line in configFile.readlines():
        line = line.rstrip()
        if not line or line.startswith('#'):
            continue  # Skip empty lines and comments
        
        section_match = section_re.match(line)
        if section_match:
            current_section = section_match.group(1)
        else:
            param_match = param_re.match(line)
            if param_match and current_section:
                param, value = param_match.group(1), param_match.group(2)
                if current_section == "Display":
                    if param == "lines":
                        display_settings[param] = int(value)
                    else:
                        display_settings[param] = value
                elif current_section == "LogFile":
                    if param == "name":
                        log_filename = value
                elif current_section == "Config":
                    if param == "debug":
                        log_level = value
    
    configFile.close()
    
    # Apply default values if any display setting is missing
    for key, default_value in display_settings.items():
        if key not in display_settings:
            display_settings[key] = default_value

    # Configure logging
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.WARNING))
    logging.info("Configuration loaded successfully")

    return display_settings, log_filename

def run():
    subnet = '188.160.0.0/12'

    display_settings, log_filename = loadConfig()

    print("Display Settings:", display_settings)
    print("Log Filename:", log_filename)

    log_lines = read_log_file(log_filename)

    log_entries = parse_log_file(log_lines)

    #print_requests_by_ip(log_entries, subnet, display_settings['lines'])

    #print_requests_by_browser(log_entries, 'Mozilla')

    #print(print_total_bytes(log_entries, display_settings['filter']))
    
if __name__ == "__main__":
    run()

