#!/usr/bin/env python
# Copyright (c) 2019 World Wide Technology, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: geo
    author: Jeff Andiorio (@jandiorio) <jandiorio(at)gmail.com>
    version_added: "2.9"
    short_description: resolve an address to latitude and longitude
    description:
        - Allows you to obtain the latitude and longitude for a given address
    options:
      address:
        description: address to resolve
        required: True
"""

EXAMPLES = """
- debug: msg="{{ lookup('geo','mullica hill, nj') }} is the lat long for Mullica Hill"
"""

RETURN = """
  _list:
    description:
      - latitude and longitude of the provided address
    type: list
"""

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError, AnsibleParserError

try:
    from geopy.geocoders import Nominatim
except ImportError as e:
    raise AnsibleError('geopy python module not installed: {}'.format(e))


class LookupModule(LookupBase):

    def run(self, address, variables, **kwargs):

        ret = []

        geolocator = Nominatim(user_agent='dnac_ansible', timeout=30)
        try:
            location = geolocator.geocode(address)
        except Exception as e:
            print(e)
            raise AnsibleParserError("Could not resolve address to lat/long:  {}".format(e))

        if location is None:
            raise AnsibleError("Lookup was unable to resolve the address provided using geopy:  {}".format(address))
        else:
            ret = [{'latitude': location.latitude, 'longitude': location.longitude}]
        return ret
