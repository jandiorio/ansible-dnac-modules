#!/usr/bin/python

import requests
import json
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

dnac_argument_spec = dict(
    host = dict(required=True, type='str'),
    port = dict(required=True, type='str'),
    username = dict(required=True, type='str'),
    password = dict(required=True, type='str'),
    #api_path = dict(required=False, default='api/v1/commonsetting/global/', type='str'),
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

        self.login()

    def login(self):

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

        #print(session.headers)

        # provide session object to functions
        return self.session

    def task_checker(self, task_id):

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

    def get_global_credentials(self, payload):

        """
            This function retrieves all credentials for the specified subType.

            Requirements:
            -------------
            You must call the session object prior to calling this function.
            A successfully established connection is required.

            Parameters:
            -----------
            session - the session object from the getSessionObj function
            dna_controller - either IP address or fqdn of the target controller
            credential_type - the type of credential to retrieve using the subTypes below

            Credential type as CLI / SNMPV2_READ_COMMUNITY /
            SNMPV2_WRITE_COMMUNITY / SNMPV3 / HTTP_WRITE /
            HTTP_READ / NETCONF
        """

        # update url for new api call
        url = "https://" + self.params['host'] + "/" + self.params['api_path']

        # set the query parameters
        self.session.params = {'credentialSubType': self.params['credential_type']}
        response = self.session.get(url)
        return response.json()

    def create_global_credential(self, payload):
        """
            This function creates a new CLI credential.

            Requirements:
            -------------
            You must call the session object prior to calling this function.
            A successfully established connection is required.

            Parameters:
            -----------
            session - the session object from the getSessionObj function
            dna_controller - either IP address or fqdn of the target controller
            cli_cred - dictionary of the parameters needed to create the credential

            dictCred = [{
                        "description":"string",
                        "username":"string",
                        "password":"string",
                        "enablePassword":"string"}
        """
        '''
        CLI / SNMPV2_READ_COMMUNITY /
        SNMPV2_WRITE_COMMUNITY / SNMPV3 / HTTP_WRITE /
        HTTP_READ / NETCONF
        '''
        _url_suffix = ''
        if self.params['credential_type'] == 'CLI':
            _url_suffix = 'cli'
        elif self.params['credential_type'] == 'SNMPV2_READ_COMMUNITY':
            _url_suffix = 'snmpv2-read-community'
        elif self.params['credential_type'] == 'SNMPV2_WRITE_COMMUNITY':
            _url_suffix = 'snmpv2-write-community'
        elif self.params['credential_type'] == 'SNMPV3':
            _url_suffix = 'snmpv3'
        elif self.params['credential_type'] == 'HTTP_WRITE':
            _url_suffix = 'http-write'
        elif self.params['credential_type'] == 'HTTP_READ':
            _url_suffix = 'http-read'
        elif self.params['credential_type'] == 'NETCONF':
            _url_suffix = 'netconf'
        #dict_creds = json.dumps(dict_creds)

        url = "https://" + self.params['host'] + "/api/v1/global-credential/" + _url_suffix
        response = self.session.request(method='POST', url=url, json=payload, verify=False)
        return response

    def update_global_credential(self, payload):

        _url_suffix = ''
        if self.params['credential_type'] == 'CLI':
            _url_suffix = 'cli'
        elif self.params['credential_type'] == 'SNMPV2_READ_COMMUNITY':
            _url_suffix = 'snmpv2-read-community'
        elif self.params['credential_type'] == 'SNMPV2_WRITE_COMMUNITY':
            _url_suffix = 'snmpv2-write-community'
        elif self.params['credential_type'] == 'SNMPV3':
            _url_suffix = 'snmpv3'
        elif self.params['credential_type'] == 'HTTP_WRITE':
            _url_suffix = 'http-write'
        elif self.params['credential_type'] == 'HTTP_READ':
            _url_suffix = 'http-read'
        elif self.params['credential_type'] == 'NETCONF':
            _url_suffix = 'netconf'
        #dict_creds = json.dumps(dict_creds)

        url = "https://" + self.params['host'] + "/api/v1/global-credential/" + _url_suffix
        response = self.session.request(method='PUT', url=url, json=payload, verify=False)
        return response

    def delete_global_credentials(self, cred_id):
        url = "https://" + self.params['host'] + "/api/v1/global-credential/" + cred_id
        response = self.session.request(method='DELETE', url=url, verify=False)
        return response

    def create_snmp_read_credential(self):

        """
            This function creates a new SNMP READ credential.

            Requirements:
            -------------
            You must call the session object prior to calling this function.
            A successfully established connection is required.

            Parameters:
            -----------
            session - the session object from the getSessionObj function
            dna_controller - either IP address or fqdn of the target controller
            snmp_read_cred - dictionary of the parameters needed to create the credential

            Example Dictionary
            ------------------
            snmp_read_cred = [
                {
                "readCommunity": "SNMP-READ-JA1",
    		    "description": "test2"
                }
            ]
        """
        print(self.params['dict_creds'])
        url = "https://" + self.params['host'] + "/api/v1/global-credential/" + self.params['path']
        response = self.session.request(method='POST', url=url, json=self.params['dict_creds'], verify=False)
        return response

    def get_common_settings(self, payload):

                url = "https://" + self.params['host'] + '/' + self.params['api_path'].rstrip('/') + '/' + payload[0]['groupUuid']
                response = self.session.request(method='GET', url=url)
                return response

    def set_common_settings(self, payload):

        """
            This function sets the global settings in the network design workflow.

            The model below is how to activate a reference to another object.  An example is
            setting which SNMP credential is used
           {
            "instanceType": "reference",
            "instanceUuid": "",
            "namespace": "global",
            "type": "reference.setting",
            "key": "credential.snmp_v2_read",
            "version": 7,
            "value": [
                {
                    "objReferences": [
                        "a31b28c4-6bcd-4667-a2e2-b74e38572498"
                    ],
                    "type": "credential_snmp_v2_read",
                    "url": ""
                }
            ],
            "groupUuid": "-1",
            "inheritedGroupUuid": "",
            "inheritedGroupName": ""
        }
        """

        url = "https://" + self.params['host'] + '/' + self.params['api_path'].rstrip('/') + '/' + payload[0]['groupUuid']
        response = self.session.request(method='POST', url=url, json=payload)
        return response

    def get_group(self, payload):

        url = "https://" + self.params['host'] + '/' + self.params['api_path'].rstrip('/')
        response = self.session.get(url)
        return response.json()


    def create_group(self, payload):

        payload = json.dumps(payload)
        url = "https://" + self.params['host'] + '/' + self.params['api_path'].rstrip('/')
        response = self.session.post(url, data=payload)
        return response

    def delete_group(self, payload):

        url = "https://" + self.params['host'] + '/' + self.params['api_path'].rstrip('/') + '/' + payload
        response = self.session.delete(url)
        return response

    def get_ippool(self, payload):

        url = 'https://' + self.params['host'] + '/' + self.params['api_path'].rstrip('/')
        response = self.session.get(url)
        return response.json()

    def create_ippool(self, payload):

        payload = json.dumps(payload)
        url = "https://" + self.params['host'] + '/' + self.params['api_path'].rstrip('/')
        response = self.session.post(url, data=payload)
        if response.status_code in [200, 201, 202]:
            response = response.json()
            task_response = self.task_checker(response['response']['taskId'])

        return task_response

    def delete_ippool(self, payload):

        url = 'https://' + self.params['host'] + '/' + self.params['api_path'].rstrip('/') + '/' + payload
        response = self.session.delete(url)
        return response


def main():
    pass

if '__name__' == '__main__':
    main()
