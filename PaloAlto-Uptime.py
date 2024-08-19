import yaml
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress only the InsecureRequestWarning from urllib3
warnings.simplefilter('ignore', InsecureRequestWarning)

def load_config(config_file):
    """Load configuration from a YAML file."""
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def get_device_info(ip, username, password):
    """Retrieve system information from a Palo Alto device."""
    url = f"https://{ip}/api/"
    params = {
        'type': 'op',
        'cmd': '<show><system><info></info></system></show>',
    }
    
    try:
        response = requests.get(url, params=params, auth=HTTPBasicAuth(username, password), verify=False)
        response.raise_for_status()
        
        # Print the full response text for debugging
        #print("Response text:", response.text)
        
        # Parse the XML response
        root = ET.fromstring(response.text)
        if root.attrib['status'] == 'success':
            # Extract and return the hostname and uptime
            hostname = root.find('.//hostname').text
            uptime = root.find('.//uptime').text
            return hostname, uptime
        else:
            print(f"Error: Command execution failed for {ip}. Status: {root.attrib['status']}")
            return None, None
    
    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred while making the request to {ip} - {e}")
        return None, None

def main():
    #Load configuration
    config = load_config('PaloAlto/PaloAltoconfig.yaml')
    
    # Extract Palo Alto credentials and devices
    username = config['palo_alto']['username']
    password = config['palo_alto']['password']
    devices = config['palo_alto']['devices']
    
    # Process each device
    for device in devices:
        ip = device['ip']
        hostname, uptime = get_device_info(ip, username, password)
        
        if hostname and uptime:
            print(f"Device IP: {ip}")
            print(f"Hostname: {hostname}")
            print(f"Uptime: {uptime}")
        else:
            print(f"Failed to retrieve information for device {ip}")

if __name__ == "__main__":
    main()
