__version__ = '0.2.0'

import zipfile
import re
import pandas as pd
import json

HIDDEN_FILE_RE = re.compile(r".*__MACOSX*")
FILE_RE = re.compile(r".*.json$")


class ColnamesDf:
    GROUPS = 'wa_groups'
    """Groups column"""

    CONTACTS = 'wa_contacts'
    """Contacts column"""


COLNAMES_DF = ColnamesDf()


def format_results(df):
    results = []
    results.append(
        {
        "id": "Whatsapp account info",
        "title": "The account information file is read:",
        "data_frame": df
        }
    )
    return results


def format_errors(errors):
    data_frame = pd.DataFrame()
    data_frame["Messages"] = pd.Series(errors, name="Messages")
    return {"id": "extraction_log", "title": "Extraction log", "data_frame": data_frame}


def extract_groups(log_error, data):

    groups_no = 0
    try:
        groups_no = len(data[COLNAMES_DF.GROUPS])
    except (TypeError, KeyError) as e:
        print("No group is available")

    if groups_no == 0:
        log_error("No group is available")

    return groups_no


def extract_contacts(log_error, data):

    contacts_no = 0

    try:
        contacts_no = len(data[COLNAMES_DF.CONTACTS])
    except (TypeError, KeyError) as e:
        print("No contact is available")

    if contacts_no == 0:
        log_error("No contact is available")
    return contacts_no


def parse_records(log_error, f):
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        log_error(f"Could not parse: {f.name}")
    else:
        return data


def parse_zipfile(log_error, zfile):
    for name in zfile.namelist():
        if name == 'whatsapp_connections/groups.json':
            if HIDDEN_FILE_RE.match(name):
                continue
            if not FILE_RE.match(name):
                continue
            data_groups = parse_records(log_error, zfile.open(name))
        elif name == 'whatsapp_connections/contacts.json':
            if HIDDEN_FILE_RE.match(name):
                continue
            if not FILE_RE.match(name):
                continue
            data_contacts = parse_records(log_error, zfile.open(name))
    return data_groups, data_contacts
    log_error("No Json file is available")


def process(file_data):
    errors = []
    log_error = errors.append
    zfile = zipfile.ZipFile(file_data)
    data_groups, data_contacts = parse_zipfile(log_error, zfile)

    if data_groups is not None:
        groups_no = extract_groups(log_error, data_groups)

    if data_contacts is not None:
        contacts_no = extract_contacts(log_error, data_contacts)

    if errors:
        return [format_errors(errors)]

    d = {'number_of_groups': [groups_no], 'number_of_contacts': [contacts_no]}
    df = pd.DataFrame(data=d)
    formatted_results = format_results(df)

    return formatted_results


if __name__ == "__main__":
    x = process('My Account Info.zip')
    print(x[0]["data_frame"])
