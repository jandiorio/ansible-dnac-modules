#!/usr/bin/env python

import requests
import json
import time
import sys
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

dnac_argument_spec = dict(
    host = dict(required=True, type='str'),
    port = dict(required=False, type='str', default='443'),
    username = dict(required=True, type='str'),
    password = dict(required=True, type='str',no_log=True),
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
        self.response = None
        self.result = dict(
            changed=False,
            original_message='',
            message='')
        self.login()


    def __setattr__(self, key, value):
        """
        Control what attributes can be attached to the object to avoid mistypes or invalid variable names.

        :param key:
        :param value:
        :return:
        """
        if key not in ['api_path', 'username', 'password', 'host', 'session', 'response', 'module','params', \
                       'cookie','credential_type', 'credential_subtype','credential_name','result']:
            raise AttributeError(key + " : Attribute not permitted")
        else:
            self.__dict__[key] = value

    # Login to DNA Center
    def login(self):
        """
        Establish a session to the DNA Center Controller.

        :return: A session object is returned.

        """

        login_url = 'https://' + self.params['host'] + '/dna/system/api/v1/auth/token'

        # create a session object
        self.session = requests.session()

        # set configuration elements
        self.session.auth = (self.params['username'], self.params['password'])
        self.session.verify = False

        # send to controller
        try:
            self.response = self.session.post(login_url)
        except Exception as e:
            self.result['changed'] = False
            self.result['original_message'] = e
            self.module.fail_json(msg='Failed to Connect to target host.', **self.result)
            
        if self.response.status_code not in [200, 201, 202]:
            self.session.close()
            self.result['changed'] = False
            self.result['original_message'] = self.response.content
            self.module.fail_json(msg='Failed to establish session. ', **self.result)
            
        # update the headers with received sessions cookies
        self.session.headers.update({'X-Auth-Token': self.response.json()['Token']})

        # set the content-type
        self.session.headers.update({'content-type' : 'application/json'})

        # provide session object to functions
        return self.session

    def intent_task_checker(self, task_id):
        """
        Obtain the status of the task based on taskId for asynchronous operations.

        :param task_id: Internal ID assigned to asynchronous tasks.

        :return: Response data from the task status lookup.
        """

        # task_checker will loop until the given task completes and return the results of the task execution
        
        url = 'https://' + self.params['host'] + '/' + 'api/dnacaap/v1/dnacaap/management/execution-status/' + task_id
        response = self.session.get(url)
        response = response.json()
        # response = response['response']

        while not response.get('endTime'):
            time.sleep(2)
            response = self.session.get(url)
            response = response.json()
            # response = response['response']

        if response.get('status') == 'SUCCESS' and response.get('bapiName').find('Update') >= 0:
            return response
        elif response.get('status') == "SUCCESS":
            self.result['changed'] = True
            self.result['original_message'] = response
            self.module.exit_json(msg='Task Completed successfully.', **self.result)
        elif response.get('status')=="FAILURE":
            self.result['changed'] = False
            self.result['original_message'] = response
            self.module.fail_json(msg='Task Failed to Complete!', **self.result)

        return response

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

        if not response.get('isError'):
            self.result['changed'] = True
            self.result['original_message'] = response
            self.module.exit_json(msg='Task completed successfully.', **self.result)
        elif response.get('isError'):
            self.result['changed'] = False
            self.result['original_message'] = response
            self.module.fail_json(msg='Task failed to complete.', **self.result)                        
        
        return response


    #generalized get object function
    def get_obj(self):
        """
        Retrieve information from the DNA Center Controller.

        :return: JSON data structure returned from a successful call or the response object.

        """

        url = 'https://' + self.params['host'] + '/' + self.api_path.rstrip('/')
        response = self.session.get(url)
        if response.status_code in [200, 201, 202]:
            try: 
                r = response.json()
                return r
            except Exception as e:
                r = []
                return r
            # if response.text.find('No_.*found'):
            #     r = []
            #     return r  
            # else:
            #     r = response.json()
            #     return r
                              
        elif response.status_code in [500]:
            # put in just for a bug in profiles get 
            if response.text.find("Profile Not Found") >= 0:
                r = []
                return r
        else:
            self.result['changed'] = False
            self.result['original_message'] = response.text
            self.module.fail_json(msg='Failed to get object!', **self.result)


    # generalized create call
    def create_obj(self, payload):
        """
        Create object in DNA Center Controller.

        :param payload: Data structure formatted for the specific call and target setting or attribute.

        :return: JSON data structure returned from a successful call or the response object.
        """
        try:
            payload = json.dumps(payload)
            # self.module.fail_json(msg=payload)
        except Exception as e: 
            self.module.fail_json(msg='failed to convert payload to json.  invalid json')
        url = "https://" + self.params['host'] + '/' + self.api_path.rstrip('/')
        
        if not self.module.check_mode:
            
            response = self.session.post(url, data=payload)
            if response.status_code in [200, 201, 202]:
                r = response.json()
                try: 
                    if url.find('intent') >= 0:
                        task_response = self.intent_task_checker(r['executionId'])
                    else: 
                        task_response = self.task_checker(r['response']['taskId'])
                        
                except Exception as e:
                    self.result['original_message'] = e
                    self.module.fail_json(msg='Failed at task_checker', **self.result)
            else:
                self.result['changed'] = False
                self.result['original_message'] = response
                self.module.fail_json(msg='Failed to create object!', **self.result)
        else: 
            self.result['changed'] = True
            self.module.exit_json(msg='In check_mode.  Changes would be required.', **self.result)


    # generalized delete call
    def delete_obj(self, payload):
        """

        :param payload: ID of the attribute to be deleted.
        :return: JSON data structure returned from a successful call or the response object.
        """
        if not self.module.check_mode:
            url = 'https://' + self.params['host'] + '/' + self.api_path.rstrip('/') + '/' + payload
            response = self.session.delete(url)
            if response.status_code in [200, 201, 202]:
                r = response.json()
                # if self.api_path.find('dna'):
                if url.find('intent') >= 0:
                    task_response = self.intent_task_checker(r['executionId'])
                else: 
                    task_response = self.task_checker(r['response']['taskId'])
            else:
                self.result['changed'] = False
                self.result['original_message'] = response.text
                self.module.fail_json(msg='Failed to create object!', **self.result)
        else: 
            self.result['changed'] = True
            self.module.exit_json(msg='In check_mode.  Changes would be required.', **self.result)


    # generalized update call
    def update_obj(self, payload):
        url = 'https://' + self.params['host'] + '/' + self.api_path.rstrip('/')
        response = self.session.request(method='PUT', url=url, json=payload, verify=False)

        if response.status_code in [200, 201, 202]:
            r = response.json()
            if url.find('intent') >= 0:
                task_response = self.intent_task_checker(r['executionId'])
            else: 
                task_response = self.task_checker(r['response']['taskId'])
                
        else:
            self.result['changed'] = False
            self.result['original_message'] = response.text
            self.module.fail_json(msg='Failed to update object!', **self.result)


    # Group ID lookup
    def get_group_id(self, group_name):

        if (self.module.params['group_name'] == '-1' or 
            self.module.params['group_name'].lower() == 'global'):
                return '-1'
        else:
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

        geolocator = Nominatim(user_agent='dnac_ansible',timeout=30)
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

    def process_common_settings(self, payload, group_id):

        if group_id:
            payload[0].update({'groupUuid': group_id})
        else:
            self.result['changed'] = False
            self.result['original_message'] = group_id
            self.module.fail_json(msg='Failed to create setting! Unable to locate group provided.', **self.result)

        # Define local variables 
        state = self.module.params['state']

        # Get current settings
        settings = self.get_obj()
        settings = settings['response']
        setting_count = len(settings)

        # Save the existing and proposed datasets
        self.result['previous'] = settings
        self.result['proprosed'] = payload
        
        if state == 'present': 
            if setting_count == 1:
            # compare previous to proposed 
                if settings[0]['value'] != payload[0]['value']:
                    self.create_obj(payload)
                else:
                    self.result['changed'] = False
                    self.result['msg'] = 'Already in desired state.'
                    self.module.exit_json(**self.result)
            elif setting_count == 0: 
                # create the object
                self.create_obj(payload)

        elif state == 'absent':
            payload[0].update({'value':[]})
            self.create_obj(payload)
def main():
    pass

if __name__ == '__main__':
    main()
