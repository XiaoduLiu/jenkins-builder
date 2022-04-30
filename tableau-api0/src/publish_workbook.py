import argparse
import math
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
import yaml
from requests.packages.urllib3.fields import RequestField
from requests.packages.urllib3.filepost import encode_multipart_formdata

from namespace import xmlns
from version import VERSION

# The maximum size of a file that can be published in a single request is 64MB
FILESIZE_LIMIT = 1024 * 1024 * 64  # 64MB

# For when a workbook is over 64MB, break it into 5MB(standard chunk size) chunks
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB


class ApiCallError(Exception):
    """ ApiCallError """
    pass


class UserDefinedFieldError(Exception):
    """ UserDefinedFieldError """
    pass


# Use UTF-8 to display messages.
def encode_for_display(text):
    return text.encode('ascii', errors="backslashreplace").decode('utf-8')


# Create parameters for execution.
def createArguments():
    parser = argparse.ArgumentParser(description='API call for publish a workbook')
    parser.add_argument("-us", "--login_username")
    parser.add_argument("-ps", "--login_password")
    parser.add_argument("-cu", "--connection_username", default="")
    parser.add_argument("-cp", "--connection_password", default="")
    parser.add_argument("-cfp", "--configuration_file_path", default="publish_workbook_settings.yaml")
    parser.add_argument("-sfp", "--server_file_path", default="servers.yaml")

    return parser


# Read parameters.
def get_user_input(parser):
    args = parser.parse_args()
    login_username = args.login_username
    login_password = args.login_password
    connection_username = args.connection_username
    connection_password = args.connection_password
    configuration_file_path = args.configuration_file_path
    server_file_path = args.server_file_path

    return login_username, login_password, connection_username, connection_password, configuration_file_path, server_file_path


# Read the file with the settings to do the deploy.
def get_configuration_file(configuration_file_path):
    with open(configuration_file_path) as f:
        configuration_file = yaml.load(f, Loader=yaml.FullLoader)
    return configuration_file


# Read the file with the servers where the files are going to be deployed.
def get_server_file(server_file_path):
    with open(server_file_path) as f:
        server_file = yaml.load(f, Loader=yaml.FullLoader)
    return server_file


# Read servers to publish.
def get_servers_to_publish(configuration_file):
    servers_to_publish = configuration_file['publish_to_server']
    return servers_to_publish


# Read files to publish.
def get_files_to_publish(configuration_file):
    files_to_publish = configuration_file['workbooks_to_publish']
    return files_to_publish


# Get project to publish to.
def get_publish_to_project(configuration_file):
    publish_to_project = configuration_file['publish_to_project']
    return publish_to_project


# Get whether files should be overwritten or not.
def get_overwrite_file_if_exists(configuration_file):
    overwrite_file_if_exists = configuration_file['overwrite_workbook_if_exists']
    return overwrite_file_if_exists

# Get whether tabbed view should be enabled or not.
def get_enable_tabbed_view(configuration_file):
    enable_tabbed_view = configuration_file['enable_tabbed_view']
    return enable_tabbed_view

# Get whether tabbed view should be enabled or not.
def get_live_connection_settings(configuration_file):

    has_live_connection = configuration_file['has_live_connection']
    
    if has_live_connection == 'true':
        server_live_connection = configuration_file['server_live_connection']
        port_live_connection = configuration_file['port_live_connection']
        embed_credentials_live_connection = configuration_file['embed_credentials_live_connection']    
    else:    
        server_live_connection = ''
        port_live_connection = ''
        embed_credentials_live_connection = ''        
    return has_live_connection, server_live_connection, port_live_connection, embed_credentials_live_connection

# Get site and url of the server where it will be published.
def get_server_information(server_file, environment):
    if environment == 'dev':
        url = server_file['dev']['url']
        site = server_file['dev']['site']
    elif environment == 'qa':
        url = server_file['qa']['url']
        site = server_file['qa']['site']
    elif environment == 'prod':
        url = server_file['prod']['url']
        site = server_file['prod']['site']
    else:
        raise LookupError("Server environment not found.")
    return url, site;


# Login to the server with the credentials entered.
def sign_in(server, username, password, site=""):
    print("Sign in into server with username: " + username)

    url = server + "/api/{0}/auth/signin".format(VERSION)

    # Creating the XML request.
    xml_request = ET.Element('tsRequest')
    credentials_element = ET.SubElement(xml_request, 'credentials', name=username, password=password)
    site_element = ET.SubElement(credentials_element, 'site', contentUrl=site)
    xml_request = ET.tostring(xml_request)

    # Make the request to server
    server_response = requests.post(url, data=xml_request)
    check_status(server_response, 200)

    # ASCII encode server response to enable displaying to console
    server_response = encode_for_display(server_response.text)

    # Reads and parses the response
    parsed_response = ET.fromstring(server_response)

    # Gets the auth token and site ID
    token = parsed_response.find('t:credentials', namespaces=xmlns).get('token')
    site_id = parsed_response.find('.//t:site', namespaces=xmlns).get('id')

    return token, site_id


# Get the project ID from the Tableau server.
def get_project_id(auth_token, server, site_id, project_name):
    page_num, page_size = 1, 100  # Default paginating values

    # Builds the request
    url = server + "/api/{0}/sites/{1}/projects".format(VERSION, site_id)
    paged_url = url + "?pageSize={0}&pageNumber={1}".format(page_size, page_num)
    server_response = requests.get(paged_url, headers={'x-tableau-auth': auth_token})

    # _check_status(server_response, 200)
    xml_response = ET.fromstring(encode_for_display(server_response.text))

    # Used to determine if more requests are required to find all projects on server
    total_projects = int(xml_response.find('t:pagination', namespaces=xmlns).get('totalAvailable'))
    max_page = int(math.ceil(total_projects / page_size))

    projects = xml_response.findall('.//t:project', namespaces=xmlns)

    # Continue querying if more projects exist on the server
    for page in range(2, max_page + 1):
        paged_url = url + "?pageSize={0}&pageNumber={1}".format(page_size, page)
        server_response = requests.get(paged_url, headers={'x-tableau-auth': auth_token})
        _check_status(server_response, 200)
        xml_response = ET.fromstring(encode_for_display(server_response.text))
        projects.extend(xml_response.findall('.//t:project', namespaces=xmlns))

    # Look through all projects to find the 'default' one
    for project in projects:
        if project.get('name') == project_name:
            return project.get('id')
    raise LookupError("Project named " + project_name + " was not found on server")


# Obtain information about the file to be published.
def get_workbook_file_information(file):
    workbook_file_path = os.path.abspath(file)
    workbook_file = os.path.basename(workbook_file_path)

    if not os.path.isfile(workbook_file_path):
        error = "{0}: file not found".format(workbook_file_path)
        raise IOError(error)

    workbook_filename, workbook_file_extension = workbook_file.split('.', 1)

    if workbook_file_extension not in ('twbx', 'twb'):
        error = "This script only accepts .twbx files to publish."
        raise UserDefinedFieldError(error)

    workbook_size = os.path.getsize(workbook_file_path)

    return workbook_file_path, workbook_file, workbook_filename, workbook_file_extension, workbook_size


# Get XML request header.
def get_publish_request(project_id, workbook_filename, enable_tabbed_view, has_live_connection, serverAddress, serverPort, connection_username, connection_password, embedCredentials):
    xml_request = ET.Element('tsRequest')
    workbook_element = ET.SubElement(xml_request, 'workbook', name=workbook_filename, showTabs=enable_tabbed_view)

    if has_live_connection == "true":        
        connections_element = ET.SubElement(workbook_element, 'connections')
        connection_element = ET.SubElement(connections_element, 'connection', serverAddress=serverAddress, serverPort=serverPort)
        connection_credentials_element = ET.SubElement(connection_element, 'connectionCredentials', name=connection_username, password=connection_password, embed=embedCredentials )
        
    project_element = ET.SubElement(workbook_element, 'project', id=project_id)
    xml_request = ET.tostring(xml_request)
    return xml_request

# Identify the publishing method that will be used to publish the files.
def get_publish_method(workbook_size):
    chunked = workbook_size >= FILESIZE_LIMIT
    return chunked


# Compress the file into small pieces.
def make_multipart(parts):
    mime_multipart_parts = []
    for name, (filename, blob, content_type) in parts.items():
        multipart_part = RequestField(name=name, data=blob, filename=filename)
        multipart_part.make_multipart(content_type=content_type)
        mime_multipart_parts.append(multipart_part)

    post_body, content_type = encode_multipart_formdata(mime_multipart_parts)
    content_type = ''.join(('multipart/mixed',) + content_type.partition(';')[1:])
    return post_body, content_type


# Validate API response with the expected response.
def check_status(server_response, success_code):
    if server_response.status_code != success_code:
        parsed_response = ET.fromstring(server_response.text)

        # Obtain the 3 xml tags from the response: error, summary, and detail tags
        error_element = parsed_response.find('t:error', namespaces=xmlns)
        summary_element = parsed_response.find('.//t:summary', namespaces=xmlns)
        detail_element = parsed_response.find('.//t:detail', namespaces=xmlns)

        # Retrieve the error code, summary, and detail if the response contains them
        code = error_element.get('code', 'unknown') if error_element is not None else 'Unknown code'
        summary = summary_element.text if summary_element is not None else 'Unknown summary'
        detail = detail_element.text if detail_element is not None else 'Unknown detail'
        error_message = '{0}: {1} - {2}'.format(code, summary, detail)
        raise ApiCallError(error_message)
    return


# Publication method, where the body of the data source is attached to the XML request.
def get_request_publish_entire_workbook(server, site_id, workbook_file_path, workbook_file, workbook_filename,
                                        workbook_file_extension, overwrite, xml_request):
    # print("\n3. Publishing '" + workbook_file + "' using the all-in-one method (workbook under 64MB)")

    # Read the contents of the file to publish
    with open(workbook_file_path, 'rb') as f:
        workbook_bytes = f.read()

        # Finish building request for all-in-one method
    parts = {'request_payload': ('', xml_request, 'text/xml'),
             'tableau_workbook': (workbook_file, workbook_bytes, 'application/octet-stream')}
    payload, content_type = make_multipart(parts)

    publish_url = server + "/api/{0}/sites/{1}/workbooks".format(VERSION, site_id)
    publish_url += "?overwrite={0}".format(overwrite)

    return payload, content_type, publish_url


# Start uploading session.
def start_upload_session(auth_token, server, site_id):
    url = server + "/api/{0}/sites/{1}/fileUploads".format(VERSION, site_id)
    server_response = requests.post(url, headers={'x-tableau-auth': auth_token})
    check_status(server_response, 201)
    xml_response = ET.fromstring(encode_for_display(server_response.text))
    uploadSessionId = xml_response.find('t:fileUpload', namespaces=xmlns).get('uploadSessionId')

    return uploadSessionId


# Method of publication, where the file is segmented into parts and then loaded through multiple uploads.
def get_request_publish_chunked_workbook(auth_token, server, site_id, workbook_file_path, workbook_file,
                                         workbook_filename, workbook_file_extension, overwrite, xml_request):
    print("\n3. Publishing '{0}' in {1}MB chunks (workbook over 64MB)".format(workbook_file, CHUNK_SIZE / 1024000))
    # Initiates an upload session
    uploadID = start_upload_session(auth_token, server, site_id)

    # URL for PUT request to append chunks for publishing
    put_url = server + "/api/{0}/sites/{1}/fileUploads/{2}".format(VERSION, site_id, uploadID)

    # Read the contents of the file in chunks of 100KB
    with open(workbook_file_path, 'rb') as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            payload, content_type = make_multipart({'request_payload': ('', '', 'text/xml'),
                                                     'tableau_file': ('file', data, 'application/octet-stream')})
            print("\tPublishing a chunk...")
            server_response = requests.put(put_url, data=payload,
                                           headers={'x-tableau-auth': auth_token, "content-type": content_type})
            check_status(server_response, 200)

    # Finish building request for chunking method
    payload, content_type = make_multipart({'request_payload': ('', xml_request, 'text/xml')})

    publish_url = server + "/api/{0}/sites/{1}/workbooks".format(VERSION, site_id)
    publish_url += "?uploadSessionId={0}".format(uploadID)
    publish_url += "&workbookType={0}&overwrite=true".format(workbook_file_extension)


# Publish the data source.
def publish_workbook(payload, content_type, publish_url, auth_token):
    # Make the request to publish and check status code
    print("\tUploading workbook to server")
    server_response = requests.post(publish_url, data=payload,
                                    headers={'x-tableau-auth': auth_token, 'content-type': content_type})
    check_status(server_response, 201)


def main():
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ": " + "Publishing process started")
    parser = createArguments()

    print("Getting user input")
    username, password, connection_username, connection_password, configuration_file_path, server_file_path = get_user_input(parser)

    print("Reading configuration files")

    configuration_file = get_configuration_file(configuration_file_path)
    server_file = get_server_file(server_file_path)

    servers_to_publish = get_servers_to_publish(configuration_file)
    files_to_publish = get_files_to_publish(configuration_file)
    publish_to_project = get_publish_to_project(configuration_file)
    overwrite_file_if_exists = get_overwrite_file_if_exists(configuration_file)
    enable_tabbed_view = get_enable_tabbed_view(configuration_file)
    has_live_connection, server_live_connection, port_live_connection, embed_credentials_live_connection = get_live_connection_settings(configuration_file)

    if not servers_to_publish:
        sys.exit('There are no servers to publish to')

    if not files_to_publish:
        sys.exit('There are no files to publish')

    print("Files to publish: " + str(len(files_to_publish)))
    print("Servers to publish: " + str(len(servers_to_publish)))

    for server in servers_to_publish:
        url, site = get_server_information(server_file, server)
        auth_token, site_id = sign_in(url, username, password, site)
        project_id = get_project_id(auth_token, url, site_id, publish_to_project)

        for file in files_to_publish:
            workbook_file_path, workbook_file, workbook_filename, workbook_file_extension, workbook_size = get_workbook_file_information(
                file)
            xml_request = get_publish_request(project_id, workbook_filename, enable_tabbed_view, has_live_connection, server_live_connection, port_live_connection, connection_username, connection_password, embed_credentials_live_connection)
            publish_method = get_publish_method(workbook_size)

            if publish_method:
                get_request_publish_chunked_workbook(auth_token, url, site_id, workbook_file_path, workbook_file,
                                                     workbook_filename, workbook_file_extension,
                                                     overwrite_file_if_exists, xml_request)
            else:
                payload, content_type, publish_url = get_request_publish_entire_workbook(url, site_id,
                                                                                         workbook_file_path,
                                                                                         workbook_file,
                                                                                         workbook_filename,
                                                                                         workbook_file_extension,
                                                                                         overwrite_file_if_exists,
                                                                                         xml_request)

            print("Publishing " + workbook_file + " into " + url + " on site: " + site)
            publish_workbook(payload, content_type, publish_url, auth_token)

    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " : " + "Publishing process finished")


if __name__ == '__main__':
    main()
