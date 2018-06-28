#!/usr/bin/python

import requests
import json
import time
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

dnac_argument_spec = dict(
    host = dict(required=True, type='str'),
    port = dict(required=False, type='str', default=443),
    username = dict(required=True, type='str'),
    password = dict(required=True, type='str'),
    use_proxy=dict(required=False, type='bool', default=True),
    use_ssl=dict(type='bool', default=True),
    timeout=dict(type='int', default=30),
    validate_certs=dict(type='bool', default=False),
    state=dict(type='str', default='present', choices=['absent', 'present', 'update', 'query'])
    )

class DnaCenter(object):

    def __init__(self, module):
        self.module = module
        self.params = module.params
        self.cookie = None
        self.session = None
        self.api_path = ''

        self.login()


    def __setattr__(self, key, value):
        """
        Control what attributes can be attached to the object to avoid mistypes or invalid variable names.

        :param key:
        :param value:
        :return:
        """
        if key not in ['api_path', 'username', 'password', 'host', 'session', 'response', 'module','params', \
                       'cookie','credential_type', 'credential_subtype','credential_name']:
            raise AttributeError(key + " : Attribute not permitted")
        else:
            self.__dict__[key] = value


    def login(self):
        """
        Establish a session to the DNA Center Controller.

        :return: A session object is returned.

        """

        login_url = 'https://' + self.params['host'] + '/api/system/v1/auth/login/'

        # Build the login_url to the API for logging into DNA
        #login_url = "https://" + dna_controller + "/api/system/v1/auth/login/"

        # create a session object
        self.session = requests.session()

        # set configuration elements
        self.session.auth = (self.params['username'], self.params['password'])
        self.session.verify = False

        # send to controller
        self.response = self.session.get(login_url)

        # update the headers with received sessions cookies
        self.session.headers.update({'cookie': self.response.headers['Set-Cookie']})

        # set the content-type
        self.session.headers.update({'content-type' : 'application/json'})

        # provide session object to functions
        return self.session

    def task_checker(self, task_id):
        """
        Obtain the status of the task based on taskId for asynchronous operations.

        :param task_id: Internal ID assigned to asynchronous tasks.

        :return: Response data from the task status lookup.
        """

        # task_checker will loop until the given task completes and return the results of the task execution
        url = 'https://' + self.params['host'] + '/' + 'api/v1/task/' + task_id
        response = self.session.get(url)
        response = response.json()
        response = response['response']

        while not response.get('endTime'):
            time.sleep(2)
            response = self.session.get(url)
            response = response.json()
            response = response['response']

        return response

    # def get_global_credentials(self):
    #
    #     """
    #         This function retrieves all credentials for the specified subType.
    #
    #         Requirements:
    #         -------------
    #         You must call the session object prior to calling this function.
    #         A successfully established connection is required.
    #
    #         Parameters:
    #         -----------
    #         session - the session object from the getSessionObj function
    #         dna_controller - either IP address or fqdn of the target controller
    #         credential_type - the type of credential to retrieve using the subTypes below
    #
    #         Credential type as CLI / SNMPV2_READ_COMMUNITY /
    #         SNMPV2_WRITE_COMMUNITY / SNMPV3 / HTTP_WRITE /
    #         HTTP_READ / NETCONF
    #     """
    #
    #     # update url for new api call
    #     url = "https://" + self.params['host'] + '/api/v1/global-credential'
    #
    #     # set the query parameters
    #     if credential_type != None:
    #         self.session.params = {'credentialSubType': credential_type }
    #     else:
    #         self.session.params = {'credentialSubType': self.params['credential_type']}
    #
    #     response = self.session.get(url)
    #     return response.json()

    # def create_global_credential(self, payload):
    #     """
    #         This function creates a new CLI credential.
    #
    #         Requirements:
    #         -------------
    #         You must call the session object prior to calling this function.
    #         A successfully established connection is required.
    #
    #         Parameters:
    #         -----------
    #         session - the session object from the getSessionObj function
    #         dna_controller - either IP address or fqdn of the target controller
    #         cli_cred - dictionary of the parameters needed to create the credential
    #
    #         dictCred = [{
    #                     "description":"string",
    #                     "username":"string",
    #                     "password":"string",
    #                     "enablePassword":"string"}
    #     """
    #     '''
    #     CLI / SNMPV2_READ_COMMUNITY /
    #     SNMPV2_WRITE_COMMUNITY / SNMPV3 / HTTP_WRITE /
    #     HTTP_READ / NETCONF
    #     '''
    #     _url_suffix = ''
    #     if self.params['credential_type'] == 'CLI':
    #         _url_suffix = 'cli'
    #     elif self.params['credential_type'] == 'SNMPV2_READ_COMMUNITY':
    #         _url_suffix = 'snmpv2-read-community'
    #     elif self.params['credential_type'] == 'SNMPV2_WRITE_COMMUNITY':
    #         _url_suffix = 'snmpv2-write-community'
    #     elif self.params['credential_type'] == 'SNMPV3':
    #         _url_suffix = 'snmpv3'
    #     elif self.params['credential_type'] == 'HTTP_WRITE':
    #         _url_suffix = 'http-write'
    #     elif self.params['credential_type'] == 'HTTP_READ':
    #         _url_suffix = 'http-read'
    #     elif self.params['credential_type'] == 'NETCONF':
    #         _url_suffix = 'netconf'
    #
    #     url = "https://" + self.params['host'] + "/api/v1/global-credential/" + _url_suffix
    #     response = self.session.request(method='POST', url=url, json=payload, verify=False)
    #     return response
    #
    # def update_global_credential(self, payload):
    #
    #     _url_suffix = ''
    #     if self.params['credential_type'] == 'CLI':
    #         _url_suffix = 'cli'
    #     elif self.params['credential_type'] == 'SNMPV2_READ_COMMUNITY':
    #         _url_suffix = 'snmpv2-read-community'
    #     elif self.params['credential_type'] == 'SNMPV2_WRITE_COMMUNITY':
    #         _url_suffix = 'snmpv2-write-community'
    #     elif self.params['credential_type'] == 'SNMPV3':
    #         _url_suffix = 'snmpv3'
    #     elif self.params['credential_type'] == 'HTTP_WRITE':
    #         _url_suffix = 'http-write'
    #     elif self.params['credential_type'] == 'HTTP_READ':
    #         _url_suffix = 'http-read'
    #     elif self.params['credential_type'] == 'NETCONF':
    #         _url_suffix = 'netconf'
    #     #dict_creds = json.dumps(dict_creds)
    #
    #     url = "https://" + self.params['host'] + "/api/v1/global-credential/" + _url_suffix
    #     response = self.session.request(method='PUT', url=url, json=payload, verify=False)
    #     return response
    # #
    # # def delete_global_credentials(self, cred_id):
    # #     url = "https://" + self.params['host'] + "/api/v1/global-credential/" + cred_id
    # #     response = self.session.request(method='DELETE', url=url, verify=False)
    # #     return response
    #
    # def create_snmp_read_credential(self):
    #
    #     """
    #         This function creates a new SNMP READ credential.
    #
    #         Requirements:
    #         -------------
    #         You must call the session object prior to calling this function.
    #         A successfully established connection is required.
    #
    #         Parameters:
    #         -----------
    #         session - the session object from the getSessionObj function
    #         dna_controller - either IP address or fqdn of the target controller
    #         snmp_read_cred - dictionary of the parameters needed to create the credential
    #
    #         Example Dictionary
    #         ------------------
    #         snmp_read_cred = [
    #             {
    #             "readCommunity": "SNMP-READ-JA1",
    # 		    "description": "test2"
    #             }
    #         ]
    #     """
    #
    #     url = "https://" + self.params['host'] + "/api/v1/global-credential/" + self.params['path']
    #     response = self.session.request(method='POST', url=url, json=self.params['dict_creds'], verify=False)
    #     return response
    #
    # def get_common_settings(self, payload):
    #
    #             url = "https://" + self.params['host'] + '/' + self.params['api_path'].rstrip('/') + '/' + payload[0]['groupUuid']
    #             response = self.session.request(method='GET', url=url)
    #             return response
    #
    # def set_common_settings(self, payload):
    #
    #     """
    #         This function sets the global settings in the network design workflow.
    #
    #         The model below is how to activate a reference to another object.  An example is
    #         setting which SNMP credential is used
    #        {
    #         "instanceType": "reference",
    #         "instanceUuid": "",
    #         "namespace": "global",
    #         "type": "reference.setting",
    #         "key": "credential.snmp_v2_read",
    #         "version": 7,
    #         "value": [
    #             {
    #                 "objReferences": [
    #                     "a31b28c4-6bcd-4667-a2e2-b74e38572498"
    #                 ],
    #                 "type": "credential_snmp_v2_read",
    #                 "url": ""
    #             }
    #         ],
    #         "groupUuid": "-1",
    #         "inheritedGroupUuid": "",
    #         "inheritedGroupName": ""
    #     }
    #     """
    #
    #     url = "https://" + self.params['host'] + '/' + self.params['api_path'].rstrip('/') + '/' + payload[0]['groupUuid']
    #     response = self.session.request(method='POST', url=url, json=payload)
    #     return response

    #generalized get object function
    def get_obj(self):
        """
        Retrieve information from the DNA Center Controller.

        :return: JSON data structure returned from a successful call or the response object.

        """

        url = 'https://' + self.params['host'] + '/' + self.api_path.rstrip('/')
        response = self.session.get(url)
        if response.status_code in [200, 201, 202]:
            r = response.json()
            return r
        else:
            return response

    # generalized create call
    def create_obj(self, payload):
        """
        Create object in DNA Center Controller.

        :param payload: Data structure formatted for the specific call and target setting or attribute.

        :return: JSON data structure returned from a successful call or the response object.
        """

        payload = json.dumps(payload)
        url = "https://" + self.params['host'] + '/' + self.api_path.rstrip('/')
        response = self.session.post(url, data=payload)

        if response.status_code in [200, 201, 202]:
            r = response.json()
            task_response = self.task_checker(r['response']['taskId'])
            return task_response
        else:
            return response

    # generalized delete call
    def delete_obj(self, payload):
        """

        :param payload: ID of the attribute to be deleted.
        :return: JSON data structure returned from a successful call or the response object.
        """

        url = 'https://' + self.params['host'] + '/' + self.api_path.rstrip('/') + '/' + payload
        response = self.session.delete(url)
        if response.status_code in [200, 201, 202]:
            r = response.json()
            task_response = self.task_checker(r['response']['taskId'])
            return task_response
        else:
            return response

    # generalized update call
    def update_obj(self, pyaload):
        url = 'https://' + self.params['host'] + '/' + self.api_path.rstrip('/')
        response = self.session.request(method='PUT', url=url, json=payload, verify=False)
        return response

    # Group ID lookup
    def get_group_id(self, group_name):

        self.api_path = 'api/v1/group'
        groups = self.get_obj()
        group_ids = [group['id'] for group in groups['response'] if group['name'] == group_name]
        if len(group_ids) == 1:
            group_id = group_ids[0]
            return group_id


    def parse_geo(self, address):
        """
        Supporting lookup addresses provided to return latitude, longitude to DNA Center.

        :param address: Physical address to lookup.

        :return: attributes dictionary
        """

        geolocator = Nominatim()
        try:
            location = geolocator.geocode(address)
        except Exception as e:
            print(e)
            sys.exit(0)

        location_parts = location.address.split(',')
        country = location_parts[len(location_parts) -1]
        attributes = {'address': location.address,
                      'country':country,
                      'latitude':location.latitude,
                      'longitude':location.longitude,
                      'type':'building'
                      }
        return attributes

    def timezone_lookup(self, address):
        """
        Provide for automated timezone resolution based on physical address provided.  Avoid long lookups or specific
        string matching.

        :param address:  Physical address of desired target timezone.
        :return: string of timezone based on address provided

        """
        location_attributes = self.parse_geo(address)
        tf = TimezoneFinder()
        tz = tf.timezone_at(lng=location_attributes['longitude'], lat=location_attributes['latitude'])
        return tz

def main():
    pass

if __name__ == '__main__':
    main()
