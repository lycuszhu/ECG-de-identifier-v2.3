import os
import xml.etree.ElementTree as ET
from faker import Faker
import random
import base64
import numpy as np
import detect_type
import csv
from datetime import datetime
from encrpt import encrypt_aes_gcm
from encrpt import key as key
# Initialize Faker
fake = Faker()

# Mindray functions
def extract_patient_info_mindray(root):
    patient_info = {}
    patient_element = root.find('.//Patient')
    if patient_element is not None:
        for child in patient_element:
            patient_info[child.tag] = child.text

    demographics_element = root.find('.//Demographics')
    if demographics_element is not None:
        for child in demographics_element:
            patient_info[child.tag] = child.text
    
    visit_number_element = root.find('.//VisitNumber')
    if visit_number_element is not None:
        patient_info['VisitNumber'] = visit_number_element.text

    return patient_info

def replace_patient_info_mindray(root, new_first_name, new_last_name, new_visit_number, new_id):
    # Replace information in <Demographics>
    demographics_element = root.find('.//Demographics')
    if demographics_element is not None:
        for child in demographics_element:
            if 'FirstName' in child.tag:
                child.text = new_first_name
            elif 'MidName' in child.tag:
                #child.text = fake.first_name()
                child.text = ""
            elif 'LastName' in child.tag:
                #child.text = new_last_name
                child.text = ""
            elif 'PatientID' in child.tag:
                child.text = new_id  # Replace ID
            elif 'VisitNumber' in child.tag:
                child.text = new_visit_number
            #elif 'DateOfBirth' in child.tag:
                #child.text = fake.date_of_birth().strftime('%Y-%m-%d')
            #elif 'Age' in child.tag:
                # Recalculate age based on new DateOfBirth
                #dob_text = demographics_element.find('DateOfBirth').text
            #     if dob_text:
            #         birth_date = datetime.strptime(dob_text, '%Y-%m-%d')
            #         today = datetime.today()
            #         age_years = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            #         child.text = f'P{age_years}Y'
            # elif 'Race' in child.tag:
            #     child.text = 'UNDEFINED'
            # elif 'BloodType' in child.tag:
            #     child.text = 'UNKNOWN'
            # elif 'Height' in child.tag:
            #     child.text = str(random.randint(150, 200))  # Random height in cm
            # elif 'Weight' in child.tag:
            #     child.text = str(random.randint(50, 100))  # Random weight in kg

    # Replace information in <AssignedLocation>
    assigned_location_element = root.find('.//AssignedLocation')
    if assigned_location_element is not None:
        for child in assigned_location_element:
            if 'Bed' in child.tag:
                child.text = fake.bothify(text='Bed ##')
            elif 'Room' in child.tag:
                child.text = fake.bothify(text='Room ###')
            elif 'PointOfCare' in child.tag:
                child.text = 'POC'
            elif 'Facility' in child.tag:
                child.text = 'Facility'
            elif 'DeviceName' in child.tag:
                child.text = 'Device'

    # Replace <Paced> if necessary
    paced_element = root.find('.//Paced')
    if paced_element is not None:
        paced_element.text = 'false'  # or leave as is

def process_mindray_file(file_path, output_path, csv_writer):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract original ID
    demographics_element = root.find('.//Demographics')
    if demographics_element is not None:
        original_id_element = demographics_element.find('PatientID')
        if original_id_element is not None:
            original_id = original_id_element.text
        else:
            original_id = None
    else:
        original_id = None

    # random_first_name = fake.first_name()
    # random_last_name = fake.last_name()

    random_first_name = ""
    random_last_name = ""

    random_visit_number = str(random.randint(1000, 9999))
    #new_id = str(fake.uuid4())
    #new_id = str(fake.pyint())
    
    new_id = str(encrypt_aes_gcm(str(original_id).encode('utf-8'),key))
    new_id_name = str(new_id)+'.XML'
    ext = '.XML'
    #print(new_id_name)
    output_path = os.path.join(output_path,new_id_name)
    #output_path = os.path.join(output_path,new_id,'.XML')

    replace_patient_info_mindray(root, random_first_name, random_last_name, random_visit_number, new_id)

    # Write original and new IDs to CSV
    try:
        if original_id is not None:
            csv_writer.writerow({'original_id': original_id, 'replaced_id': new_id})
    except UnicodeEncodeError as e:
        print(f"⚠️ Skipping file due to encoding error: {file_path} — {e}")
        return

    # Save the modified XML tree to the output path
    tree.write(output_path)

def update_patient_info_philips(root, namespace, new_id):
    # Find and update name
    name = root.find('.//ns:patient/ns:generalpatientdata/ns:name', namespace)
    if name is not None:
        last_name_element = name.find('ns:lastname', namespace)
        if last_name_element is not None:
            # last_name_element.text = fake.last_name()
            last_name_element.text = ""

        first_name_element = name.find('ns:firstname', namespace)
        if first_name_element is not None:
            # first_name_element.text = fake.first_name()
            first_name_element.text = ""
        middle_name_element = name.find('ns:middlename', namespace)
        if middle_name_element is not None:
            # middle_name_element.text = fake.first_name()
            middle_name_element.text = ""


    # Find and update bed number
    acquirer = root.find('.//ns:dataacquisition/ns:acquirer', namespace)
    if acquirer is not None:
        bed_element = acquirer.find('ns:bed', namespace)
        if bed_element is not None:
            bed_element.text = fake.bothify(text='Bed ##')

    # # Find and update date of birth
    # age = root.find('.//ns:patient/ns:generalpatientdata/ns:age', namespace)
    # if age is not None:
    #     dob_element = age.find('ns:dateofbirth', namespace)
    #     if dob_element is not None:
    #         dob_element.text = fake.date_of_birth(minimum_age=0, maximum_age=100).strftime('%Y-%m-%d')

    # Find and update patient ID
    patientid_element = root.find('.//ns:patient/ns:generalpatientdata/ns:patientid', namespace)
    if patientid_element is not None:
        patientid_element.text = new_id

    # Update MRN and secondary ID if present
    general_patient_data = root.find('.//ns:patient/ns:generalpatientdata', namespace)
    if general_patient_data is not None:
        mrn_element = general_patient_data.find('ns:MRN', namespace)
        if mrn_element is not None:
#            mrn_element.text = fake.bothify(text='MRN####')
            mrn_element.text = ""
            #print("MRN Updated")

        secondary_id_element = general_patient_data.find('ns:secondaryid', namespace)
        if secondary_id_element is not None:
            secondary_id_element.text = fake.bothify(text='SecID####')


def process_philips_file(file_path, output_path, csv_writer):
    namespace = {'ns': 'http://www3.medical.philips.com'}
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract original ID
    patientid_element = root.find('.//ns:patient/ns:patientid', namespace)
    if patientid_element is not None:
        original_id = patientid_element.text
    else:
        original_id = None

    #new_id = str(fake.uuid4())
    new_id = str(encrypt_aes_gcm(str(original_id).encode('utf-8'),key))

    # new_id = str(fake.pyint())
    new_id_name = str(new_id)+'.XML'
    #print(new_id_name)
    output_path = os.path.join(output_path,new_id_name)
    # output_path = os.path.join(output_path,new_id,'.XML')


    update_patient_info_philips(root, namespace, new_id)

    # Write original and new IDs to CSV
    try:
        if original_id is not None:
            csv_writer.writerow({'original_id': original_id, 'replaced_id': new_id})
    except UnicodeEncodeError as e:
        print(f"⚠️ Skipping file due to encoding error: {file_path} — {e}")
        return

    # Save the modified XML tree to the output path
    tree.write(output_path)

# Mortara functions
def replace_patient_info_mortara(root, new_id):
    # new_first_name = fake.first_name()
    # new_last_name = fake.last_name()

    new_first_name = ""
    new_last_name = ""
    # new_dob = fake.date_of_birth().strftime("%Y%m%d")

    demographic_fields = root.find(".//DEMOGRAPHIC_FIELDS")
    if demographic_fields:
        for field in demographic_fields.findall("DEMOGRAPHIC_FIELD"):
            id_tag = field.get('ID')
            if id_tag == "1":  # Last Name
                field.set('VALUE', new_last_name)
            elif id_tag == "7":  # First Name
                field.set('VALUE', new_first_name)
            elif id_tag == "2":  # Patient ID  
                field.set('VALUE', new_id)
            # elif id_tag == "16":  # Date of Birth
            #     field.set('VALUE', new_dob)
    
    subject = root.find(".//SUBJECT")
    if subject is not None:
        subject.set("LAST_NAME", new_last_name)
        subject.set("FIRST_NAME", new_first_name)
        subject.set("ID", new_id)
        # subject.set("DOB", new_dob)

def process_mortara_file(file_path, output_path, csv_writer):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract original ID
    subject = root.find(".//SUBJECT")
    if subject is not None:
        original_id = subject.get("ID")
    else:
        original_id = None

    #new_id = str(fake.uuid4())
    # new_id = str(fake.pyint())
    new_id = str(encrypt_aes_gcm(str(original_id).encode('utf-8'),key))
    # new_id = str(fake.random_number(digits=8, fix_len=True))
    new_id_name = str(new_id)+'.XML'
    #print(new_id_name)
    output_path = os.path.join(output_path,new_id_name)

    replace_patient_info_mortara(root, new_id)

    # Write original and new IDs to CSV
    try:
        if original_id is not None:
            csv_writer.writerow({'original_id': original_id, 'replaced_id': new_id})
    except UnicodeEncodeError as e:
        print(f"⚠️ Skipping file due to encoding error: {file_path} — {e}")
        return

    # Save the modified XML tree to the output path
    tree.write(output_path)


# Main function to process files based on the device name
def process_files_in_folder(input_folder, output_folder):
    print(f"Input Folder: {input_folder}")
    print(f"Output Folder: {output_folder}")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(('.txt', '.xml','XML')):
            file_path = os.path.join(input_folder, filename)
            print(f'file_path {file_path}')
            output_path = os.path.join(output_folder, filename)
            
            device_name = detect_type.detect_device_type(file_path)
            device_name_lower = device_name.lower()
            if device_name_lower == 'mindray':
                process_mindray_file(file_path, output_path)
                print(f"Processed {filename} as {device_name}")
            elif device_name_lower == 'philips':
                process_philips_file(file_path, output_path)
                print(f"Processed {filename} as {device_name}")
            elif device_name_lower == 'mortara':
                process_mortara_file(file_path, output_path)
                print(f"Processed {filename} as {device_name}")
            else:
                print(f"Unknown device name: {device_name}")

            print('Done processing.\n')


# Internal processing functions that handle CSV writing internally
def process_mindray_file_internal(filename_, file_path, output_path, csv_writer, key):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract original ID
    demographics_element = root.find('.//Demographics')
    if demographics_element is not None:
        original_id_element = demographics_element.find('PatientID')
        if original_id_element is not None:
            original_id = original_id_element.text
        else:
            original_id = None
    else:
        original_id = None

    # random_first_name = fake.first_name()
    # random_last_name = fake.last_name()

    random_first_name = ""
    random_last_name = ""

    random_visit_number = str(random.randint(1000, 9999))
    #new_id = str(fake.uuid4())
    # new_id = str(fake.pyint())
    new_id = str(encrypt_aes_gcm(str(original_id).encode('utf-8'),key))
    # new_id = str(fake.random_number(digits=8, fix_len=True))

    new_id_name = filename_ + '.XML'

    #new_id_name = str(new_id)+'.XML'
    #print(new_id_name)
    output_path = os.path.join(output_path,new_id_name)
    # output_path = os.path.join(output_path,new_id,'.XML')


    replace_patient_info_mindray(root, random_first_name, random_last_name, random_visit_number, new_id)

    # Write original and new IDs to CSV
    try:
        if original_id is not None:
            csv_writer.writerow({'original_id': original_id, 'replaced_id': new_id})
    except UnicodeEncodeError as e:
        print(f"⚠️ Skipping file due to encoding error: {file_path} — {e}")
        return

    # Save the modified XML tree to the output path
    tree.write(output_path)

def process_philips_file_internal(filename_, file_path, output_path, csv_writer, key):
    namespace = {'ns': 'http://www3.medical.philips.com'}
    tree = ET.parse(file_path)
    root = tree.getroot()
    #print(f'Tree {tree}, root {root}')

    # Extract original ID
    patientid_element = root.find('.//ns:patient/ns:generalpatientdata/ns:patientid', namespace)
    #print(f'Extracted patient id element: {patientid_element}')
    if patientid_element is not None:
        original_id = patientid_element.text
    else:
        original_id = None

    #new_id = str(fake.uuid4())
    # new_id = str(fake.pyint())
    # new_id = str(fake.random_number(digits=8, fix_len=True))
    new_id = str(encrypt_aes_gcm(str(original_id).encode('utf-8'),key))

    # new_id_name = str(new_id)+'.XML'
    new_id_name = filename_ + '.XML'
    #print(new_id_name)
    output_path = os.path.join(output_path,new_id_name)
    # output_path = os.path.join(output_path,new_id,'.XML')


    update_patient_info_philips(root, namespace, new_id)

    # Write original and new IDs to CSV
    try:
        if original_id is not None:
            csv_writer.writerow({'original_id': original_id, 'replaced_id': new_id})
    except UnicodeEncodeError as e:
        print(f"⚠️ Skipping file due to encoding error: {file_path} — {e}")
        return
    # Save the modified XML tree to the output path
    tree.write(output_path)


def process_mortara_file_internal(filename_, file_path, output_path, csv_writer, key):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract original ID
    subject = root.find(".//SUBJECT")
    if subject is not None:
        original_id = subject.get("ID")
    else:
        original_id = None

    #new_id = str(fake.uuid4())
    #new_id = str(fake.pyint())
    #new_id = str(fake.random_number(digits=8, fix_len=True))
    new_id = str(encrypt_aes_gcm(str(original_id).encode('utf-8'),key))

    # new_id_name = str(new_id)+'.XML'
    new_id_name = filename_ + ".XML"
    #print(new_id_name)
    output_path = os.path.join(output_path,new_id_name)
    #print(output_path)
    # output_path = os.path.join(output_path,new_id,'.XML')


    replace_patient_info_mortara(root, new_id)

    # Write original and new IDs to CSV
    try:
        if original_id is not None:
            csv_writer.writerow({'original_id': original_id, 'replaced_id': new_id})
    except UnicodeEncodeError as e:
        print(f"⚠️ Skipping file due to encoding error: {file_path} — {e}")
        return

    # Save the modified XML tree to the output path
    tree.write(output_path)

# External functions that can be called without csv_writer
def process_mindray_file(filename_, file_path, output_path):
    csv_file_path = os.path.join(output_path, "id_mappings.csv")
    print(f'csv_file_path = {csv_file_path}')
    file_exists = os.path.exists(csv_file_path)
    with open(csv_file_path, mode='a', newline='') as csvfile:
        fieldnames = ['original_id', 'replaced_id']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists or os.stat(csv_file_path).st_size == 0:
            csv_writer.writeheader()
        process_mindray_file_internal(filename_, file_path, output_path, csv_writer, key)

def process_philips_file(filename_, file_path, output_path):
    csv_file_path = os.path.join(output_path, "id_mappings.csv")
    file_exists = os.path.exists(csv_file_path)
    with open(csv_file_path, mode='a', newline='') as csvfile:
        fieldnames = ['original_id', 'replaced_id']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists or os.stat(csv_file_path).st_size == 0:
            csv_writer.writeheader()
        process_philips_file_internal(filename_, file_path, output_path, csv_writer, key)

def process_mortara_file(filename_, file_path, output_path):
    csv_file_path = os.path.join(output_path, "id_mappings.csv")
    file_exists = os.path.exists(csv_file_path)
    with open(csv_file_path, mode='a', newline='') as csvfile:
        fieldnames = ['original_id', 'replaced_id']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists or os.stat(csv_file_path).st_size == 0:
            csv_writer.writeheader()
        process_mortara_file_internal(filename_, file_path, output_path, csv_writer, key)

if __name__=="__main__":
    input_folder = './input'
    output_folder = './output'

    process_files_in_folder(input_folder, output_folder)
