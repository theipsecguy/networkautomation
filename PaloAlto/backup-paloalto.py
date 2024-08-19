import requests
import yaml
from requests.auth import HTTPBasicAuth
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import paramiko
import os
from datetime import datetime

# Suppress only the InsecureRequestWarning from urllib3
warnings.simplefilter('ignore', InsecureRequestWarning)

def load_config(config_file):
    """Load configuration from a YAML file."""
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def get_running_config(ip, username, password):
    """Retrieve the running configuration from the Palo Alto firewall."""
    url = f"https://{ip}/api/"
    params = {
        'type': 'export',
        'category': 'configuration',
    }
    
    try:
        response = requests.get(url, params=params, auth=HTTPBasicAuth(username, password), verify=False)
        response.raise_for_status()
        
        # The configuration is returned in XML format
        config_xml = response.text
        return config_xml
    
    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred while making the request to {ip} - {e}")
        return None

def save_config_to_sftp(config_xml, hostname, sftp_host, sftp_username, sftp_password, base_remote_path):
    """Save the configuration XML to the SFTP server in a date-based directory."""
    try:
        # Establish an SFTP connection
        transport = paramiko.Transport((sftp_host, 22))
        transport.connect(username=sftp_username, password=sftp_password)
        
        # Open an SFTP session
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Create a folder with the current date
        date_folder = datetime.now().strftime('%Y-%m-%d')
        remote_path = os.path.join(base_remote_path, date_folder)
        
        # Ensure the date-based directory exists
        try:
            sftp.stat(remote_path)
        except FileNotFoundError:
            sftp.mkdir(remote_path)
        
        # Define the remote file path within the date-based folder
        remote_file_path = os.path.join(remote_path, f"{hostname}_running_config.xml")
        
        # Write the configuration XML to the remote file
        with sftp.file(remote_file_path, 'w') as file:
            file.write(config_xml)
        
        print(f"Configuration successfully saved to {remote_file_path} on the SFTP server")
        
        # Close the SFTP connection
        sftp.close()
        transport.close()
        
    except Exception as e:
        print(f"Error: Failed to save configuration to SFTP server - {e}")

def main():
    # Load configuration from YAML file
    config = load_config('PaloAlto/PaloAltoconfig.yaml')
    
    # Extract credentials
    username = config['palo_alto']['username']
    password = config['palo_alto']['password']
    devices = config['palo_alto']['devices']
    
    # SFTP server details
    sftp_host = '10.255.10.140'
    sftp_username = 'sftp-username'
    sftp_password = 'sftp-password'
    base_remote_path = '/home/yourpath/PaloAltoBackups'  # Update this to your base path on the SFTP server
    
    # Process each device
    for device in devices:
        ip = device['ip']
        hostname = device['hostname']
        
        # Retrieve the running configuration
        config_xml = get_running_config(ip, username, password)
        
        if config_xml:
            # Save the configuration to the SFTP server in a date-based folder
            save_config_to_sftp(config_xml, hostname, sftp_host, sftp_username, sftp_password, base_remote_path)

if __name__ == "__main__":
    main()
