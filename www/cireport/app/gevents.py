#!/usr/bin/python
from bson import ObjectId
from datetime import datetime
import json
import sys
import urllib
import pdb
import pymongo
import re

from app import collection

import conf

class MongoDocumentEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder(self, o)


def mongodoc_jsonify(*args, **kwargs):
    return json.dumps(dict(*args, **kwargs),indent=4, cls=MongoDocumentEncoder)

class CIReport(object):

    def __init__(self, ci, project, sentiment):
        self.ci = ci
        self.project = project
        self.sentiment = sentiment
        if self.project == 'openstack/nova':
            self.users = conf.CI_USERS_NOVA
        elif self.project == 'openstack/neutron':
            self.users = conf.CI_USERS_NEUTRON
        self.users.append('Total')


    def build_query(self, sentiment):
        query = {"_id.ci":
                        {
                         "$in" : self.users
                        },
                 "_id.project": self.project
                 # ,
                # "patchsets.x":{'$gt':1395273600}

            }
        query2={
                "patchsets."+sentiment : {"$ne": 0}
        }
        projection = {
                    '_id.ci':1,
                    '_id.project':1,
                    'patchsets.date': {'$multiply':['$patchsets.date' , 1000]},
                    'patchsets.'+sentiment : 1
            }

        groupby = {
                    '_id':{'$concat':['$_id.ci','__',sentiment]},
                    'patchsets':{
                                '$addToSet':{
                                                'y':'$patchsets.'+sentiment,
                                                'x':'$patchsets.date'
                                }

                    }
                }

        """play area for dygraph"""
        groupby2 = {
                    '_id':'$patchsets.date'
                    ,
                    'patchsets':{
                                '$addToSet':{
                                                'x':{'$concat':['$_id.ci','__',sentiment]},
                                                'y':'$patchsets.'+sentiment
                                }

                    }
                }

        return [
        {'$match' : query}
        ,{'$unwind':'$patchsets'}
        ,{'$match':query2}
         ,{'$project' : projection }
           ,{'$group' : groupby}
         ]


    def get_all_ci_results(self):
        aggr = []
        aggr_s = collection.aggregate(self.build_query('positive'))['result']
        aggr_f = collection.aggregate(self.build_query('negative'))['result']
        aggr_m = collection.aggregate(self.build_query('missing'))['result']
        aggr_t = collection.aggregate(self.build_query('exists'))['result']

        aggr = aggr_s + aggr_f + aggr_m + aggr_t

        present_users = [x['_id'] for x in aggr]

        for user in self.users:
            if user == 'Total':
                continue
            for sent in ['__positive','__negative','__missing']:
                if user + sent not in present_users:
                    filler =  { '_id':user + sent,
                                'patchsets':[{'y':0,'x':aggr[0]['patchsets'][0]['x']},
                                {'y':0,'x':aggr[0]['patchsets'][-1]['x']}
                                ]
                            }

                    aggr.append(filler)

        granularity_value = 60*60*0.5
        for ci in aggr:
            ci['patchsets'] = sorted(ci['patchsets'], key = lambda patchset: patchset['x'])
            ci['patchsets'] = self.complete_dataset(ci['patchsets'],granularity_value*10000)
        return aggr


    def time_units(self,start_date, stop_date, timeunit):
        start = start_date
        while start_date + timeunit < stop_date:
            yield start_date, start_date + timeunit
            start_date = start_date + timeunit


    def complete_dataset(self, dataset, timeunit):
        array = [dataset[0]]
        data_prev = dataset[0]
        for i in range(len(dataset) - 1):
            data_now = dataset[i+1]
            for start_date, start_date in self.time_units(
                    data_prev['x'], data_now['x'], timeunit):
                array.append({
                    'y': 0,
                    'x': start_date
                })
            array.append(data_now)
            data_prev = data_now
        return array
