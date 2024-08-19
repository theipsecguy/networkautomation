import yaml
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Suppress only the InsecureRequestWarning from urllib3
warnings.simplefilter('ignore', InsecureRequestWarning)

def load_config(config_file):
    """Load configuration from a YAML file."""
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def get_license_info(ip, username, password):
    """Retrieve license information from a Palo Alto device."""
    url = f"https://{ip}/api/"
    params = {
        'type': 'op',
        'cmd': '<request><license><info></info></license></request>',
    }
    
    try:
        response = requests.get(url, params=params, auth=HTTPBasicAuth(username, password), verify=False)
        response.raise_for_status()
        
        # Parse the XML response
        root = ET.fromstring(response.text)
        if root.attrib['status'] == 'success':
            licenses = []
            for entry in root.findall('.//entry'):
                feature = entry.find('feature').text
                expires = entry.find('expires').text
                expired = entry.find('expired').text
                status = "Expired" if expired == "yes" else "Valid"
                licenses.append([feature, status, expires])
            return licenses
        else:
            print(f"Error: Command execution failed for {ip}. Status: {root.attrib['status']}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error: An error occurred while making the request to {ip} - {e}")
        return None

def generate_pdf(report_data, output_file):
    """Generate a PDF report from the license information."""
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    elements = []
    
    # Table header
    data = [["Hostname", "IP Address", "Feature", "Status", "Expires"]]
    
    for device_info in report_data:
        hostname = device_info['hostname']
        ip = device_info['ip']
        licenses = device_info['licenses']

        if licenses:
            for license_info in licenses:
                feature, status, expires = license_info
                data.append([hostname, ip, feature, status, expires])
        else:
            data.append([hostname, ip, "N/A", "Failed to retrieve", "N/A"])
    
    # Creating table
    table = Table(data, colWidths=[1.5 * inch] * 5)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    doc.build(elements)

def main():
    # Load configuration
    config = load_config('PaloAlto/PaloAltoconfig.yaml')
    
    # Extract Palo Alto credentials and devices
    username = config['palo_alto']['username']
    password = config['palo_alto']['password']
    devices = config['palo_alto']['devices']
    
    report_data = []

    # Process each device
    for device in devices:
        hostname = device['hostname']
        ip = device['ip']
        licenses = get_license_info(ip, username, password)
        report_data.append({'hostname': hostname, 'ip': ip, 'licenses': licenses})
    
    # Generate PDF report
    generate_pdf(report_data, "license_status_report.pdf")

if __name__ == "__main__":
    main()
