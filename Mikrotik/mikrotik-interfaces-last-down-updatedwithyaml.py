import paramiko
import yaml

# Load router configuration from the YAML file
with open('Mikrotiks/mikrotik-inventory.yaml', 'r') as file:
    config = yaml.safe_load(file)

username = config['palo_alto']['username']
password = config['palo_alto']['password']
devices = config['palo_alto']['devices']

interface_name = 'pppoe-out1'  # Replace with the name of the interface you want to check

def check_last_down_time(device):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device['ip'], port=22, username=username, password=password)

        # Execute the command to get detailed information about the interface
        command = f'/interface print detail where name={interface_name}'
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()

        # Initialize last_down_time
        last_down_time = "Not available"

        # Process the output
        for line in output.splitlines():
            if 'last-link-down-time=' in line:
                # Extract the value for last-link-down-time
                parts = line.split('last-link-down-time=')
                if len(parts) > 1:
                    last_down_time = parts[1].strip()
                    break

        # Print the result with the hostname included
        print(f"Hostname: {device['hostname']}, Router IP: {device['ip']}, Interface: {interface_name}, Last Link Down Time: {last_down_time}")
        ssh.close()

    except Exception as e:
        print(f"An error occurred on router {device['hostname']} ({device['ip']}): {e}")

# Iterate over each device and check the interface status
for device in devices:
    check_last_down_time(device)
