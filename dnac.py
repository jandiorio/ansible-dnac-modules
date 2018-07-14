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

    # Login to DNA Center
    def login(self):
        """
        Establish a session to the DNA Center Controller.

        :return: A session object is returned.

        """

        login_url = 'https://' + self.params['host'] + '/api/system/v1/auth/token/'

        # create a session object
        self.session = requests.session()

        # set configuration elements
        self.session.auth = (self.params['username'], self.params['password'])
        self.session.verify = False

        # send to controller
        self.response = self.session.post(login_url)

        # update the headers with received sessions cookies
        self.session.headers.update({'X-Auth-Token': self.response.json()['Token']})

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
    def update_obj(self, payload):
        url = 'https://' + self.params['host'] + '/' + self.api_path.rstrip('/')
        response = self.session.request(method='PUT', url=url, json=payload, verify=False)

        if response.status_code in [200, 201, 202]:
            r = response.json()
            task_response = self.task_checker(r['response']['taskId'])
            return task_response
        else:
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
