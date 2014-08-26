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
import pdb
import conf
import re
import json
import paramiko
import pymongo
import sys
import pdb
import datetime
from datetime import datetime
import gevent
from time import sleep
from bson.code import Code

from oslo.config import cfg

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

# LOG = logging.getLogger(__name__)


def get_mongodb_db():
    # LOG.info("Connecting to MongoDB")
    client = pymongo.MongoClient(CONF.mongodb_hostname, CONF.mongodb_port)
    db = client[CONF.mongodb_db]
    return db


def get_mongodb_events_coll():
    # LOG.info("Connecting to MongoDB")
    client = pymongo.MongoClient(CONF.mongodb_hostname, CONF.mongodb_port)
    db = client[CONF.mongodb_db]
    return db[CONF.mongodb_collection]

filters = {
            'XenServer CI' : ['^(Failed using)','^(Passed using)'],
            'Big Switch CI' : ['^(doesn\'t seem to work)','^(Build succe*)'],
            'Arista Testing' : ['Arista.*FAILED','^(Build succe*)'],
            'default' : [ '^(Build failed.)', '^(Build succe*)']
}


def filter_data(data):
    if 'approvals' in data.keys():
        for approval in data['approvals']:
            if approval.get('value') in ['1', '2']:
                data['positive'] = 1
            elif approval.get('value') in ['-1', '-2']:
                data['negative'] = 1
        data.pop('approvals')
    if data['author']['name'] in filters.keys():
        if re.compile(filters[data['author']['name']][0]).match(data['comment']):
                data['negative'] = 1
        elif len(filters[data['author']['name']]) > 1 and re.compile(filters[data['author']['name']][1]).match(data['comment']):
                data['positive'] = 1
    else:
         if re.compile(filters['default'][0]).match(data['comment']):
                data['negative'] = 1
         elif re.compile(filters['default'][1]).match(data['comment']):
                data['positive'] = 1


    return data

period_transl = {
'15mins': 0.25,
'full_30mins3': 0.5,
'full_30mins4': 0.5,
'1hour': 1,
'4hours': 4,
'1day':  24,
'1week': 24*7,
'4weeks': 24*7*4
}

def create_median_collection(period_p):
    db = pymongo.Connection(CONF.mongodb_hostname)[CONF.mongodb_db]
    col = db[CONF.mongodb_collection]

    period = period_transl[period_p]
    print period
    query = {

                 "change.branch":'master',
                 "change.project": { '$in' : conf.CI_PROJECTS }

            }

    projection = {
                  'positive' : 1,
                  'patchSet.createdOn' : 1,
                  'missing' :1,
                  'exists' :1,
                  'patchSet.ref':1,
                  'author.name' : 1,
                  'negative': 1,
                  'change.project': 1,
                }

    groupby2 = { '_id' : {'ci':'$_id.title','project':'$_id.project'},
                'patchsets' :{
                            '$push':{
                                         'positive':'$positive',
                                         'negative':'$negative',
                                         'missing':'$missing',
                                         'exists':'$exists',
                                         'date':{'$multiply':[ '$_id.date',period * 3600]},
                                         'refs':'$refs'
                                         }
                             }
                 }


    groupby1 = { '_id': { 'date': { '$subtract' :[ {'$divide' : ['$patchSet.createdOn', 3600*period ]}, { '$mod' : [{'$divide' : ['$patchSet.createdOn', 3600*period ]},1] } ] },
                'title':{'$concat':['$author.name']},
                'project':'$change.project',
                },
                'positive':
                        {
                    '$sum':'$positive'
                        },

                'negative':{
                        '$sum':'$negative'
                     },

                'missing':{
                        '$sum':'$missing'
                     },

                'exists':{
                        '$sum':'$exists'
                     },

                 'refs':{'$addToSet':{'ref':'$patchSet.ref'}}

             }

    aggr = col.aggregate([{'$match':query},{'$project':projection}
        ,{'$group':groupby1}
         ,{'$group':groupby2}
        ])['result']
    for res in aggr:
        db[period_p].update({'_id':res['_id']}, res, upsert=True)

def create_median_collectionv2(period_p='full_30minsv2'):
    ###TODO###
    """
    we get document of form _id{ci:hyper_v,project:nova}, patchsets[231]
    extract patchsets array
    order patchsets by patchset.createdOn
    save current createdOn
    iterate through each patchset and see if  next patchset.createdOn <current+30min 
        add missing/positive to current createdOn and append to current.refs the refs
    when next patchset.createdOn > current+30min , it becomes next current createdOn
    insert the document in full_30mins4

    """
    db = pymongo.Connection(CONF.mongodb_hostname)[CONF.mongodb_db]
    col = db[CONF.mongodb_collection]

    # period = period_transl[period_p]

    query = {    "change.branch":'master',
                 "change.project": {'$in': conf.CI_PROJECTS },
                 "author.name":{'$in':conf.CI_USERS_NOVA}
            }
    projection = {'positive' : 1,
                  'patchSet.createdOn' : 1,
                  'missing' :1,
                  'exists' :1,
                  'patchSet.ref':1,
                  'author.name' : 1,
                  'negative': 1,
                  'change.project': 1
                  }
    groupby = {'_id': { 'ci':'$author.name',
                        'project':'$change.project'},

                 'patchsets':{'$push': {'patchset':'$patchSet',
                                            'positive':'$positive',
                                            'negative':'$negative',
                                            'missing':'$missing'}
                                }
                }

    aggr = col.aggregate([{'$match':query},{'$project':projection}
        ,{'$group':groupby}
        ])['result']

    for res in aggr:

        ordered_patchsets = sorted(res['patchsets'], key = lambda elem: elem['patchset']['createdOn'])

        aggregated_patchset = []

        current_bunch_patchset = ordered_patchsets[0]
        increment  = False
        current_bunch_date = ordered_patchsets[0]['patchset']['createdOn']
        current_bunch_patchset['date'] = current_bunch_date
        current_bunch_patchset['refs'] = []
        current_bunch_patchset['refs'].append(ordered_patchsets[0]['patchset']['ref'])
        
        for key in ['missing','positive','negative','exists']:
            if current_bunch_patchset.get(key) is None:
                current_bunch_patchset[key] = 0


        for pset in ordered_patchsets:
            if increment:
                aggregated_patchset.append(current_bunch_patchset)
                current_bunch_date = pset['patchset']['createdOn']
                current_bunch_patchset = pset
                current_bunch_patchset['date'] = current_bunch_date
                current_bunch_patchset['refs'] = []
                current_bunch_patchset['refs'].append(pset['patchset']['ref'])

                for key in ['missing','positive','negative','exists']:
                    if current_bunch_patchset.get(key) is None:
                        current_bunch_patchset[key] = 0
                increment = False
            if pset['patchset']['createdOn'] > current_bunch_date + 60*30:
                increment = True
            else:
                for key in ['missing','positive','negative','exists']:
                    current_bunch_patchset[key] += pset.get(key,0)
                current_bunch_patchset['refs'].append(pset['patchset']['ref'])
        aggregated_patchset.append(current_bunch_patchset)

        res['patchsets'] = aggregated_patchset
        db[period_p].update({'_id':res['_id']}, res, upsert=True)



recheck_dict = {
   'Hyper-V CI' : 'recheck hyper-v' ,
   'IBM PowerKVM Testing' : 'recheck pkvm',
   'XenServer CI' : 'recheck xenserver',
   'VMware Mine Sweeper' : 'recheck-vmware',
   'turbo-hipster' : 'recheck-migrations',
   'Big Switch CI' : 'recheck-bigswitch'
   # ,'default' : '(recheck.*bug?)|(reverify)'
   ## MAKE DEFAULT A REGEX FOR recheck.*bug

}


def compute_missing_patchsets( project='openstack/nova' ):


    db = get_mongodb_db()
    map = Code("""
     function() {
                emit(
                this.patchSet.ref,
                { 'data': [{'comment':this.comment, 'author': this.author.name , 'createdOn' :this.patchSet.createdOn }]
                }
                );
        }
        """)

    reduce = Code("""
        function(key, values) {
                var reduced = {"data":[]};
                values.forEach(function(val){
                    reduced['data'].push(val['data'][0]);
                    });
        return reduced;
        }
  """)

    db[CONF.mongodb_collection].remove({'missing':{'$exists':True},'change.project':project})
    #res = db[CONF.mongodb_collection].inline_map_reduce(map=map,reduce=reduce,query={ "change.project" : project}, jsMode=True)
    db[CONF.mongodb_collection].map_reduce(map=map,reduce=reduce,out={'replace':'temp_collection'},query={ "change.project" : project}, jsMode=True)

    unique_ps = []
    res = db['temp_collection'].find()
    temp_result = []
    for result in res:
            result['rev_number'] = int(result['_id'].split('/')[-2])
            result['patchset_number'] = int(result['_id'].split('/')[-1])
            if result['rev_number']+result['patchset_number'] not in unique_ps:
                unique_ps.append(result['rev_number']+result['patchset_number'])
                print str(result['rev_number'])+'/'+ str(result['patchset_number'])
            temp_result.append(result)

    temp_result.sort(key = lambda i: (i['rev_number'] , i['patchset_number']))
    to_file_dump = []

    for position, patchset in enumerate(temp_result):
        val  = patchset['value']
        if type(val) == type([]):
            data = val[0]['data']
            # print len(val)
        else:
            data = val['data']
        patchsetDate = data[0]['createdOn']
        if position+1 < len(temp_result) and temp_result[position+1]['rev_number'] == patchset['rev_number'] :
            if type(temp_result[position+1]['value']) == type([]):
                temp_data = temp_result[position+1]['value'][0]['data']
                # print len(val)
            else:
                temp_data = temp_result[position+1]['value']['data']

            valid_for = temp_data[0]['createdOn'] - patchsetDate


           #CHECK IF PATCH WAS VALID FOR LESS THAN 3HR
            if valid_for < 60*60*3 :
                continue
        fresh_for = datetime.utcnow() - datetime.utcfromtimestamp(int(patchsetDate))
        # print "#### " , position
        # print fresh_for
        # print fresh_for.total_seconds()
        if fresh_for.total_seconds() < 60*60*3:
            continue

        base_event = {'author':{'name':'Total'},'exists': 1 , 'patchSet':{'createdOn':int(patchsetDate), 'ref':patchset['_id']},
                'change':{'project':project,'branch':'master'},'comment':'exists'}

        db[CONF.mongodb_collection].update(base_event, base_event, upsert=True)


        expected_results = {}
        real_results = {}
        if project == 'openstack/nova':
            users = conf.CI_USERS_NOVA
        elif project == 'openstack/neutron':
            users = conf.CI_USERS_NEUTRON
        for u in users:
            expected_results[u] = 0
            real_results[u] = 0
        expected_results['default'] = 1

        missing_hash = {}
        if type(val) == type([]):
            data = patchset['value'][0]['data']
        else:
            data = patchset['value']['data']
            

        for suite in data:

            if 'comment' not in suite.keys():
                continue
            
            # print suite, '\n' , expected_results , '\n' , real_results , '\n'

            global_recheck = True
            for k,v in recheck_dict.iteritems():
                if suite['comment'].startswith(v) and  suite['author'] in expected_results.keys() and suite['author'] != 'Elastic Recheck':
                    expected_results[k] += 1
                    global_recheck = False
                """

                TODO: GLOBALIZE THIS
                recheck pkvm -> IBM PowerKVM Testing
                recheck xenserver -> XenServer CI
                """

            if global_recheck:
                import re

                if re.compile('((recheck.*bug?.[0-9]*)$)|(reverify$)|((reverify.*bug?.[0-9]*)$)').search(suite['comment']) and suite['author'] != 'Elastic Recheck':
                    expected_results['default'] += 1
                # if 'recheck' in suite['comment'] and not suite['author'] in expected_results.keys() and suite['author'] != 'Elastic Recheck':
                #     expected_results['default'] += 1
                # elif 'reverify' in suite['comment'] and not suite['author'] in expected_results.keys() and suite['author'] != 'Elastic Recheck':
                #     expected_results['default'] += 1

            """
             IDEA: SWAP OUT RECHECK FOR JENKINS 'starting check jobs'
            elif 'Starting check jobs.' in suite['comment']:
                expected_results['default'] += 1
            """
            if suite['author'] in real_results.keys() and not re.compile('(Starting check jobs.)|(Starting gate jobs.)').match(suite['comment']) and not (suite['comment'] == 'missing'):
                real_results[suite['author']] += 1

        # if patchset['_id'] == 'refs/changes/08/84308/1':
        #     pdb.set_trace()
        # if suite['createdOn'] == 1398126640:
        #         import pdb
        #         pdb.set_trace()
        for key in real_results.keys():
            if real_results[key] < expected_results[key]+expected_results['default']:
                missing_hash[key] = expected_results[key]+expected_results['default'] - real_results[key]



        # for misses in missing_hash:

        if len(missing_hash.keys()) > 0:
            # print missing_hash , patchsetDate
            for  key in missing_hash:
                missing_event = {'author':{'name':key},'missing':missing_hash[key], 'patchSet':{'createdOn':int(patchsetDate), 'ref':patchset['_id']},
                'change':{'project':project,'branch':'master'},'comment':'missing'}

                db[CONF.mongodb_collection].update(missing_event, missing_event, upsert=True)

def main():
    # # CONF(sys.argv[1:])
    proj = 'openstack/nova'
    compute_missing_patchsets(proj)

    proj = 'openstack/neutron'
    compute_missing_patchsets(proj)

    create_median_collection('full_30mins3')

def debug():
    create_median_collectionv2()
    
if __name__ == "__main__":
    #debug()
    # main()
    while True:
        try:
            sleep(60*30)
            main()
            sleep(60*60*4)
        except:
            continue
