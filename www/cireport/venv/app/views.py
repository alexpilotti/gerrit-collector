from bson import ObjectId
from datetime import datetime
import json

from gevents import CIReport

import flask
import pymongo

from app import app
from flask import Response, jsonify, request

class MongoDocumentEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder(self, o)


def mongodoc_jsonify(*args, **kwargs):
    return Response(json.dumps(dict(*args, **kwargs), cls=MongoDocumentEncoder), mimetype='application/json')


@app.route('/')
def index():
    content = '<p>Generating chart...<p>'
    return flask.render_template('main.html', content=content)

@app.route('/<string:style>')
def index2(style):
    if style == 'cloudbase':
        content = '<p>Generating chart...<p>'
        return flask.render_template('main.html', content=content)
    elif style =='bare':
        content = '<p>Generating chart...<p>'
        return flask.render_template('main_bare.html', content=content)


@app.route('/api/events/<string:ci>')
def get_events(ci):
    print ci
    project = 'openstack/'+ci
    status = 'negative'
    rep = CIReport(ci, project, status)
    result = rep.get_all_ci_results()
    if len(result) > 0:
        return mongodoc_jsonify({'title':'all','CIs' : result})
    return mongodoc_jsonify([])
