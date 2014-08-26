#!/usr/bin/env python
# Copyright 2014 Cloudbase Solutions Srl
# All Rights Reserved.
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

import conf
import re
import json
import paramiko
import pymongo
import sys
import pdb
import datetime
import gevent
from time import sleep
from oslo.config import cfg

import sys
import urllib

import conf
# import utilities
# from collector.openstack.common import log as logging

opts = [
    cfg.StrOpt('ssh_private_key_path', default=None,
               help='SSH key used to connect to Gerrit'),
    cfg.StrOpt('ssh_username', default=None,
               help='Gerrit SSH username'),
    cfg.StrOpt('ssh_hostname', default='review.openstack.org',
               help='Gerrit SSH host'),
    cfg.IntOpt('ssh_port', default=29418,
               help='Gerrit SSH port'),
    cfg.StrOpt('mongodb_hostname', default='127.0.0.1',
               help='MongoDB host'),
    cfg.IntOpt('mongodb_port', default=27017,
               help='MongoDB port'),
    cfg.StrOpt('mongodb_db', default='gerrit-collector',
               help='MongoDB db'),
    cfg.StrOpt('mongodb_collection', default='full_events3',
               help='MongoDB events collection'),
]

CONF = cfg.CONF
CONF.register_opts(opts)

import requests

filters = {
            'XenServer CI' : ['(Failed using)','(Passed using)'],
            'Big Switch CI' : ['(doesn\'t seem to work)','(Build succe*)'],
            'Arista Testing' : ['Arista.*FAILED','(Build succe*)'],
            'default' : [ '(Build failed.)', '(Build succe*)']
}


def filter_data(data):
    # pdb.set_trace()
    if 'approvals' in data.keys():
        for approval in data['approvals']:
            if approval.get('value') in ['1', '2']:
                data['positive'] = 1
            elif approval.get('value') in ['-1', '-2']:
                data['negative'] = 1
        data.pop('approvals')
    if data['author']['name'] in filters.keys():
        if re.compile(filters[data['author']['name']][0]).search(data['comment']):
                data['negative'] = 1
        elif len(filters[data['author']['name']]) > 1 and re.compile(filters[data['author']['name']][1]).search(data['comment']):
                data['positive'] = 1
    else:
         if re.compile(filters['default'][0]).search(data['comment']):
                data['negative'] = 1
         elif re.compile(filters['default'][1]).search(data['comment']):
                data['positive'] = 1

    return data

def get_mongodb_events_coll():
    client = pymongo.MongoClient(CONF.mongodb_hostname, CONF.mongodb_port)
    db = client[CONF.mongodb_db]
    return (db[CONF.mongodb_collection],db['raw_data'])

def start():
    day = datetime.datetime.now()
    day -= datetime.timedelta(days=15)
    (new_events, raw_data) = get_mongodb_events_coll()
    while day < datetime.datetime.now():
        print 'Processing %s/%s/%s' % (day.year, day.month, day.day)
        url = 'http://www.rcbops.com/gerrit/merged/%s/%s/%s' % (day.year, day.month, day.day)
        print url
        r = requests.get(url)

        for line in r.iter_lines():
            try:
                j = json.loads(line)
    #            if j['patchSet']['ref'] =='refs/changes/37/91137/2' and j['author']['name'] == 'Hyper-V CI':
     #               pdb.set_trace()
                filtered_data = filter_data(j)
                if filtered_data['patchSet']['createdOn'] > int((datetime.datetime.now()-datetime.timedelta(days=15)).strftime('%s')):
                    new_events.update(filtered_data, filtered_data, upsert=True)
                    raw_data.update(j, j, upsert=True)
            except:
                continue
        day += datetime.timedelta(days=1)

if __name__ == '__main__':
#    while True:
#        try:
    start()
#            sleep(60*60*4)
#        except:
#            continue
