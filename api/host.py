#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, request
import jimit as ji

from models import Database as db
from models import Utils, Rules, Host
from models.initialize import app


__author__ = 'James Iter'
__date__ = '2017/5/30'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


blueprint = Blueprint(
    'api_host',
    __name__,
    url_prefix='/api/host'
)

blueprints = Blueprint(
    'api_hosts',
    __name__,
    url_prefix='/api/hosts'
)


@Utils.dumps2response
def r_nonrandom(hosts_name, random):

    args_rules = [
        Rules.HOSTS_NAME.value
    ]

    try:
        ji.Check.previewing(args_rules, {args_rules[0][1]: hosts_name})

        if str(random).lower() in ['false', '0']:
            random = False

        else:
            random = True

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        Host.set_allocation_mode(hosts_name=hosts_name.split(','), random=random)

        ret['data'] = Host.get_all()
        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get(nodes_id):

    args_rules = [
        Rules.IDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {args_rules[0][1]: nodes_id})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        if -1 == nodes_id.find(','):
            node_id = nodes_id
            if db.r.hexists(app.config['hosts_info'], node_id):
                v = json.loads(db.r.hget(app.config['hosts_info'], node_id))
                v = Host.alive_check(v)
                v['node_id'] = node_id
                ret['data'] = v

        else:
            for node_id in nodes_id.split(','):
                if db.r.hexists(app.config['hosts_info'], node_id):
                    v = json.loads(db.r.hget(app.config['hosts_info'], node_id))
                    v = Host.alive_check(v)
                    v['node_id'] = node_id
                    ret['data'].append(v)

            if ret['data'].__len__() > 1:
                ret['data'].sort(key=lambda _k: _k['boot_time'])

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_get_by_filter():

    try:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        alive = None

        if 'alive' in request.args:
            alive = request.args['alive']

            if str(alive).lower() in ['false', '0']:
                alive = False

            else:
                alive = True

        for host in Host.get_all():
            if alive is not None and alive is not host['alive']:
                continue

            ret['data'].append(host)

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_content_search():
    keyword = request.args.get('keyword', '')

    args_rules = [
        Rules.KEYWORD.value
    ]

    try:
        ji.Check.previewing(args_rules, {'keyword': keyword})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        for host in Host.get_all():
            if -1 != host['hostname'].find(keyword):
                ret['data'].append(host)

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_delete(nodes_id):

    args_rules = [
        Rules.IDS.value
    ]

    try:
        ji.Check.previewing(args_rules, {args_rules[0][1]: nodes_id})

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        if -1 == nodes_id.find(','):
            node_id = nodes_id
            if db.r.hexists(app.config['hosts_info'], node_id):
                v = json.loads(db.r.hget(app.config['hosts_info'], node_id))
                v['node_id'] = node_id
                ret['data'] = v
                db.r.hdel(app.config['hosts_info'], node_id)

        else:
            for node_id in nodes_id.split(','):
                if db.r.hexists(app.config['hosts_info'], node_id):
                    v = json.loads(db.r.hget(app.config['hosts_info'], node_id))
                    v['node_id'] = node_id
                    ret['data'].append(v)
                    db.r.hdel(app.config['hosts_info'], node_id)

            if ret['data'].__len__() > 1:
                ret['data'].sort(key=lambda _k: _k['boot_time'])

        return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)

