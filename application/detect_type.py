import xml.etree.ElementTree as ET

def detect_device_type(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    source = root.find('SOURCE')
    #print(source)

    # Namespace handling
    namespaces = {
        'philips': 'http://www3.medical.philips.com',
        'mortara': 'http://www.mortara.com',
        'mindray': 'http://www.mindray.com'
    }
    
    # Try Philips
    document_type = root.find('.//philips:documenttype', namespaces)
    if document_type is not None and document_type.text in ('PhilipsECG', 'SierraECG'):
        return 'Philips'

    # Try Mortara
    if source is not None and 'Mortara' in source.get('MANUFACTURER', ''):
        return 'Mortara'

    # Try Mindray
    if root.find('Header') is not None:
    # document_type = root.find('.//mindray:documenttype', namespaces)
    # if document_type is not None and document_type.text == 'MindrayECG':
        return 'Mindray'

    return 'Unknown'

def process_file(file_path):
    device_type = detect_device_type(file_path)
    #print(f"Processing {file_path} as {device_type} device.")
    # Add your processing code here based on the device type

# Example usage
# file_paths = [
#     '/home/rapids/echo_deiden/flask_testing_2/ABC1234_2010-01-05_22-17-59 Mortara file.txt',
#     '/home/rapids/echo_deiden/flask_testing_2/ABC1234_2016-10-09_16-28-49 Philips file.txt',
#     '/home/rapids/echo_deiden/flask_testing_2/ABC1234_2021-09-27_21-53-39 Mindray file.txt'
#     ]

# for file_path in file_paths:
#     process_file(file_path)
