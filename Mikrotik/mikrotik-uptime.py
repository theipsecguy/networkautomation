import paramiko
import yaml

# Load router configuration from the YAML file
with open('Mikrotiks/mikrotik-inventory.yaml', 'r') as file:
    config = yaml.safe_load(file)

username = config['palo_alto']['username']
password = config['palo_alto']['password']
devices = config['palo_alto']['devices']

def check_last_down_time(device):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device['ip'], port=22, username=username, password=password)

        # Execute the command to get uptime information
        command = '/system resource print'
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()

        # Initialize uptime
        uptime = "Not available"

        # Process the output to find uptime
        for line in output.splitlines():
            if 'uptime: ' in line:
                # Extract the value for uptime
                parts = line.split('uptime: ')
                if len(parts) > 1:
                    uptime = parts[1].strip()
                    break

        print(f"Hostname: {device['hostname']}, Router IP: {device['ip']}, Uptime: {uptime}")
        ssh.close()

    except Exception as e:
        print(f"An error occurred on router {device['ip']}: {e}")

# Iterate over each router and check the uptime
for device in devices:
    check_last_down_time(device)
