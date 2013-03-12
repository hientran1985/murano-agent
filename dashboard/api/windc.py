# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import urlparse

from django.utils.decorators import available_attrs
from portasclient.v1.client import Client as windc_client


LOG = logging.getLogger(__name__)


def windcclient(request):
    url = "http://127.0.0.1:8082"
    LOG.debug('windcclient connection created using token "%s" and url "%s"'
              % (request.user.token, url))
    return windc_client(endpoint=url, token=request.user.token.token['id'])


def datacenters_create(request, parameters):
    name = parameters.get('name', '')
    return windcclient(request).environments.create(name)


def datacenters_delete(request, datacenter_id):
    return windcclient(request).environments.delete(datacenter_id)


def datacenters_get(request, datacenter_id):
    return windcclient(request).environments.get(datacenter_id)


def datacenters_list(request):
    return windcclient(request).environments.list()

def datacenters_deploy(request, datacenter_id):
    session_id = windcclient(request).sessions.list(datacenter_id)[0].id
    return windcclient(request).sessions.deploy(datacenter_id, session_id)

def services_create(request, datacenter, parameters):
    LOG.critical("////////////////////////////////")
    LOG.critical(parameters)
    LOG.critical("////////////////////////////////")
    session_id = windcclient(request).sessions.list(datacenter)[0].id
    if parameters['service_type'] == 'active directory':
        res = windcclient(request).activeDirectories.create(datacenter, session_id, parameters)
    else:
        res = windcclient(request).webServers.create(datacenter, session_id, parameters)
        
    return res


def services_list(request, datacenter_id):
    session_id = request.user.token.token['id']
    services = []
    
    sessions = windcclient(request).sessions.list(datacenter_id)
    for s in sessions:
        if s.state == 'open':
            windcclient(request).sessions.delete(datacenter_id, s.id)
    
    session_id = windcclient(request).sessions.configure(datacenter_id).id
    services = windcclient(request).activeDirectories.list(datacenter_id, session_id)
    services += windcclient(request).webServers.list(datacenter_id, session_id)
    
    return services


def services_get(request, datacenter, service_id):
    LOG.critical("********************************")
    LOG.debug(parameters)
    LOG.critical("********************************")
    return windcclient(request).services.get(datacenter, service_id)


def services_delete(request, datacenter, service_id):
    return windcclient(request).services.delete(datacenter, service_id)
