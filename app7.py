import re
import logging
import json
import sys
from ipaddress import IPv4Address

logger = logging.getLogger(__name__)

configurations = { 
    'logName' :'file.txt',
    'myIpAddress' : '192.168.0.0',
    'loggingLevel' : 10,
    'linesAtOnce' : 10,
    'maxSize' : 2137 
}

def loadConfig():
    display_settings = {
        "lines": "10",      # Default value for lines
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
        print(line)
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
    display_settings, log_filename = loadConfig()
    #print("Display Settings:", display_settings)
    #print("Log Filename:", log_filename)
    

if __name__ == "__main__":
    run()

