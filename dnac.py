#!/usr/local/bin

from ansible.module_utils._text import to_bytes
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, open_url
from ansible.module_utils.basic import json
from ansible.module_utils._text import to_native

dnac_argument_spec = dict(
    hostname=dict(type='str', required=True, aliases=['host']),
    username=dict(type='str', default='admin', aliases=['user']),
    password=dict(type='str', required=True, no_log=True),
    timeout=dict(type='int', default=30),
    use_proxy=dict(type='bool', default=True),
    use_ssl=dict(type='bool', default=True),
    validate_certs=dict(type='bool', default=True)
)

def dnac_response_error(result):
    ''' Set error information when found '''
    result['error_code'] = 0
    result['error_text'] = 'Success'
    # Handle possible DNAC error information
    if result['totalCount'] != '0':
        try:
            result['error_code'] = result['imdata'][0]['error']['attributes']['code']
            result['error_text'] = result['imdata'][0]['error']['attributes']['text']
        except (KeyError, IndexError):
            pass

def dnac_response_json(result, rawoutput):
    ''' Handle DNAC JSON response output '''
    try:
        result.update(json.loads(rawoutput))
    except Exception as e:
        # Expose RAW output for troubleshooting
        result.update(raw=rawoutput, error_code=-1, error_text="Unable to parse output as JSON, see 'raw' output. %s" % e)
        return

    # Handle possible DNAC error information
    dnac_response_error(result)


class DNACModule(object):

    def __init__(self, module):
        self.module = module
        self.params = module.params
        self.result = dict(changed=False)
        self.headers = None

        self.login()

    def define_protocol(self):
        ''' Set protocol based on use_ssl parameter '''

        # Set protocol for further use
        if self.params['protocol'] is None:
            self.params['protocol'] = 'https' if self.params.get('use_ssl', True) else 'http'
        else:
            self.module.fail_json(msg="Parameter 'protocol' needs to be one of ( http, https )")

    def define_method(self):
        ''' Set method based on state parameter '''

        # Handle deprecated method/action parameter
        if self.params['method']:
            # Deprecate only if state was a valid option
            if 'state' in self.module.argument_spec:
                self.module.deprecate("Parameter 'method' or 'action' is deprecated, please use 'state' instead", '2.6')
            method_map = dict(delete='absent', get='query', post='present')
            self.params['state'] = method_map[self.params['method']]
        else:
            state_map = dict(absent='delete', present='post', query='get')
            self.params['method'] = state_map[self.params['state']]

    def login(self):

        ''' Log in to DNAC '''

        # Ensure protocol is set (only do this once)
        self.define_protocol()

        try:
            authurl = '{0}://{1}/api/system/v1/auth/login'.format(protocol, module.params['host'])
            authresp = open_url(authurl,
                                headers=authheaders,
                                method='GET',
                                use_proxy=module.params['use_proxy'],
                                timeout=module.params['timeout'],
                                validate_certs=module.params['validate_certs'],
                                url_username=module.params['username'],
                                url_password=module.params['password'],
                                force_basic_auth=True
                                )
        except Exception as e:
            module.fail_json(msg=e)

        if to_native(authresp.read()) != "success":  # DNA Center returns 'success' in the body
            module.fail_json(msg="Authentication failed: {}".format(authresp.read()))

        respheaders = authresp.getheaders()
        cookie = None

        for i in respheaders:
            if i[0] == 'Set-Cookie':
                cookie_split = i[1].split(';')
                cookie = cookie_split[0]

        if cookie is None:
            module.fail_json(msg="Cookie not assigned from DNA Center")

        headers['Cookie'] = cookie

        print(authresp.read())

if '__name__' == '__main__':
    mod_args = {}
    mod_args['params'] = {'timeout':'30',
                        'use_proxy': True,
                        'method': "GET",
                        'state':'present',
                        'username':'admin',
                        'password':'M0bility@ccess',
                        'host':'10.253.176.237'
                        }
    dnac = DNACModule(mod_args)
