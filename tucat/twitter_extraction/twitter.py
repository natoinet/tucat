from __future__ import absolute_import

import json
from datetime import datetime
from collections import defaultdict
import logging
import logging.config
import threading
import time
import queue

from celery import task
from celery.app.task import Task

from django.http import HttpResponse

import requests
from requests_oauthlib import OAuth1
import pymongo
from pymongo import MongoClient
from django.conf import settings

from tucat.core.token import get_app_token, get_users_token
from tucat.core.celery import app
from tucat.core.apilimit import ApiLimitFunction
from tucat.application.models import TucatApplication

logger = logging.getLogger('twitter_extraction')

DATE_START = datetime.utcnow()

PAGING_NAME = 'cursor'
PAGING_KEY = 'next_cursor'
REMAINING_KEY = 'x-rate-limit-remaining'
RESET_EPOCH_KEY = 'x-rate-limit-reset'

all_users = set()
all_users_following_id = defaultdict(set)
all_users_follower_id = defaultdict(set)
top_users = set()
db_name = __package__.replace('.', '_')
colname = None

def drop_collection(database, collection):
    logger.debug('Drop collection %s', database)
    
    client = MongoClient(settings.MONGO_CLIENT)
    db = client[database]
    db.drop_collection(collection)

def get_collection(database, collection):
    logger.debug('get collection %s from database %s', collection, database)
    
    client = MongoClient(settings.MONGO_CLIENT)
    db = client[database]

    logger.debug('return database %s collection %s', database, collection)
    
    return db[collection]

def get_status(src_json, key1, key2):
    result = None
    
    result = src_json.get(key1, None)
    if (result is not None):
        result = result.get(key2, None)
    
    return result


def get_user_dict(screen_name, top_user, json_user, following, follower):
    user_dict = {'screenname' : screen_name,
        'name' : json_user.get('name', None),
        'topuser' : top_user,
        'id' : json_user.get('id', None),
        'description' : json_user.get('description', None),
        'verified' : json_user.get('verified', None),
        'createdat' : json_user.get('created_at', None),
        'protected' : json_user.get('protected', None),
        'url' : json_user.get('url', None),
        'followerscount' : json_user.get('followers_count', None),
        'listedcount' : json_user.get('listed_count', None),
        'statusescount' : json_user.get('statuses_count', None),
        'friendscount' : json_user.get('friends_count', None),
        'favouritescount' : json_user.get('favourites_count', None),
        'following' : following,
        'follower' : follower,
        'notifications' : json_user.get('notifications', None),
        'contributorsenabled' : json_user.get('contributors_enabled', None),
        'followrequestsent' : json_user.get('follow_request_sent', None),
        'lang' : json_user.get('lang', None),
        'timezone' : json_user.get('time_zone', None),
        'utcoffset' : json_user.get('utc_offset', None),
        'location' : json_user.get('location', None),
        'geoenabled' : json_user.get('geo_enabled', None),
        'istranslator' : json_user.get('is_translator', None),
        'defaultprofile' : json_user.get('default_profile', None),
        'defaultprofileimage' : json_user.get('default_profile_image', None),
        'profileusebackgroundimage' : json_user.get('profile_use_background_image', None),
        'profileimageurl' : json_user.get('profile_image_url', None),
        'profiletextcolor' : json_user.get('profile_text_color', None),
        'profilelinkcolor' : json_user.get('profile_link_color', None),
        'profilebackgroundimageurl' : json_user.get('profile_background_image_url', None),
        'profilebackgroundcolor' : json_user.get('profile_background_color', None),
        'profilebackgroundtile' : json_user.get('profile_background_tile', None),
        'profilesidebarfillcolor' : json_user.get('profile_sidebar_fill_color', None),
        'profilesidebarbordercolor' : json_user.get('profile_sidebar_border_color', None),
        'statuscreatedat' : get_status(json_user, 'status', 'created_at'),
        'statustext' : get_status(json_user, 'status', 'text'),
        'statusfavorited' : get_status(json_user, 'status', 'favorited'),
        'statusretweeted' : get_status(json_user, 'status', 'retweeted'),
        'statusretweetcount' : get_status(json_user, 'status', 'retweet_count'),
        'statustruncated' : get_status(json_user, 'status', 'truncated'),
        'statusinreplytoscreenname' : get_status(json_user, 'status', 'in_reply_to_screen_name'),
        'statussource' : get_status(json_user, 'status', 'source'),
        'statusplace' : get_status(json_user, 'status', 'place'),
        'statusgeo' : get_status(json_user, 'status', 'geo')}
    
    return user_dict


def add_user_to_mongo(screen_name, top_user, json_user, following, follower):
    global db_name
    global colname

    logger.debug('add_user_to_mongo')

    user_dict = get_user_dict(screen_name, top_user, json_user, following, follower)      
    collection_extraction = get_collection(db_name, colname)
    collection_extraction.insert(user_dict)

    logger.debug('add_user_to_mongo %s OK', screen_name)


def addTopUsersToResults(url, parameters, res_status_code, res_json):
    global all_users
    global top_users
    global db_name
    
    logger.info('addTopUsersToResults url: %s - parameters: %s status_code: %s', url, len(parameters), res_status_code)
    
    if (res_status_code is not 200):
        logger.warning('addTopUsersToResults NOT 200 url: %s - parameters: %s status_code: %s', url, len(parameters), res_status_code)
        return
        
    users_results = get_collection(db_name, 'users_results')

    for one_user_json in res_json['users']:
        user_result = {'date': DATE_START,
            'user_id' : one_user_json['id'],
            'screen_name' : one_user_json['screen_name'],
            'json_result' : one_user_json,
            'top_user' : True}

        top_users.add(one_user_json['screen_name'])

        users_results.insert(user_result)


def addAllUsersToResults(url, parameters, res_status_code, res_json):
    global all_users_following_id
    global all_users_follower_id
    global current_function
    
    logger.info('addAllUsersToResults url: %s parameters: %s status_code: %s', url, len(parameters), res_status_code)
    
    current_function = None
    
    if (res_status_code is not 200):
        logger.warning('addAllUsersToResults NOT 200 url: %s - parameters: %s status_code: %s', url, len(parameters), res_status_code)
        return
        
    users_results = get_collection(db_name, 'users_results')

    for one_user_json in res_json:
        #Check for existence for not overwriting top users
        if (users_results.find_one({'date': DATE_START, 'screen_name' : one_user_json['screen_name']}) is None):
            # Is not a top user => Insert new document in database
            logger.debug('addAllUsersToResults insert new one_user_json: %s',
                one_user_json['screen_name'])

            user_result = {'date': DATE_START,
                'user_id' : one_user_json['id'],
                'screen_name' : one_user_json['screen_name'],
                'json_result' : one_user_json,
                'following' : list(all_users_following_id[one_user_json['id']]),
                'follower' : list(all_users_follower_id[one_user_json['id']]),
                'top_user' : False}
            #users_results.insert(user_result)

            #add_user_to_gdata_collection(user_result['screen_name'], False, user_result['json_result'], 
            #    user_result['following'], user_result['follower'])
            add_user_to_mongo(user_result['screen_name'], False, user_result['json_result'], 
                user_result['following'], user_result['follower'])

        else:
            # Is a top user => update existing document in collection
            logger.debug('addAllUsersToResults update existing one_user_json: %s',
                one_user_json['screen_name'])
        
            following = list(all_users_following_id[one_user_json['id']])
            follower = list(all_users_follower_id[one_user_json['id']])
        
            #users_results.update({'date': DATE_START, 'user_id' : one_user_json['id']},
            #    { "$set" : {'following' : following, 'follower' : follower}})

            #add_user_to_gdata_collection(one_user_json['screen_name'], True, one_user_json, 
            #    following, follower)
            add_user_to_mongo(one_user_json['screen_name'], True, one_user_json, 
                following, follower)


def addRelationToResults(url, parameters, res_status_code, res_json):
    global all_users
    global all_users_following_id
    global all_users_follower_id
    global current_function

    logger.info('addRelationToResults url: %s parameters: %s status_code: %s', url, parameters, res_status_code)

    current_function = None

    if (res_status_code is not 200):
        logger.warning('addRelationToResults NOT 200 url: %s - parameters: %s status_code: %s', url, len(parameters), res_status_code)
        return
        
    relation_type = None
    if (url == 'https://api.twitter.com/1.1/followers/ids.json'):
        relation_type = 'followers_id'
    elif (url == 'https://api.twitter.com/1.1/friends/ids.json'):
        relation_type = 'following_id'

    #relation_list contains the list of followers or friends for a specific user
    relation_list = res_json['ids']

    logger.debug('addRelationToResults url: %s - parameters: %s - relation type: %s \nRelation list: %s',
                    url, parameters, relation_type, relation_list)

    users_results = get_collection(db_name, 'users_results')
    #print parameters['screen_name'], relation_type, ','.join(map(str, relation_list))
    users_results.update({'screen_name': parameters['screen_name']}, {"$set": {relation_type : relation_list}})

    all_users.update(relation_list)

    #user is a follower if in top users following list and inversely
    for each_user_id in relation_list:
        if (relation_type is 'followers_id'):
            logger.debug('addRelationToResults all_users_following_id %s', 
                all_users_following_id[each_user_id])
            all_users_following_id[each_user_id].add(parameters['screen_name'])
        
        elif (relation_type is 'following_id'):
            logger.debug('addRelationToResults all_users_following_id %s', 
                all_users_follower_id[each_user_id])
            all_users_follower_id[each_user_id].add(parameters['screen_name'])


def get_hundred_ids():
    global all_users
    
    parameters = []
    count = 1
    print (len(all_users))
    #Find a way using a subset to retrieve only 100 at a time then move to the next one!
    while len(all_users) > (count - 1) * 100:
        start = 100 * (count - 1)
        end = 100 * count
        hundred_ids = ','.join(map(str, list(all_users)[start:end]))
        logger.debug('url Hundred Ids: %s', hundred_ids)

        parameters.append({'user_id' : hundred_ids})    
        count += 1

    logger.debug('get_hundred_ids parameters: %s', parameters)

    return parameters

def tw_extraction(owner_name='', list_name='', collection_name=''):
    global db_name
    global colname
    colname = collection_name

    logger.info('tw_extraction start %s %s', owner_name, list_name)
    
    current_function = None
    app_token = get_app_token('twitter')
    users_token = get_users_token ('twitter')

    """Start"""
    force_stop = False
    drop_collection(db_name, 'users_results')

    '''
    if (force_stop is True):
        return
    '''

    """Extract Top users"""
    url = 'https://api.twitter.com/1.1/lists/members.json'
    parameters = [{'owner_screen_name' : owner_name, 'slug' : list_name}]    
    logger.info('parameters %s', parameters)
    #current_function = ApiLimitFunction(url, CONSUMER, TOKENS, parameters, PAGING_NAME, PAGING_KEY, REMAINING_KEY, RESET_EPOCH_KEY, addTopUsersToResults, {200 : 'ok', 401 : 'ok', 429 : 'wait'})
    current_function = ApiLimitFunction(url, app_token, users_token, parameters, PAGING_NAME, PAGING_KEY, REMAINING_KEY, RESET_EPOCH_KEY, addTopUsersToResults, {200 : 'ok', 401 : 'ok', 429 : 'wait'})
    #_queue.put(*current_function)
    current_function.run()

    logger.info('tw_extraction post_members')

    '''
    if (force_stop is True):
        return
    '''

    """Extract Followers ids"""
    url = 'https://api.twitter.com/1.1/followers/ids.json'
    parameters_followers = []
    for user_id in top_users:
        parameters_followers.append({'screen_name' : user_id})
    parameters_friends = list(parameters_followers)

    #current_function = ApiLimitFunction(url, CONSUMER, TOKENS, parameters_followers, PAGING_NAME, PAGING_KEY, REMAINING_KEY, RESET_EPOCH_KEY, addRelationToResults, {200 : 'ok', 401 : 'ok', 429 : 'wait'})
    current_function = ApiLimitFunction(url, app_token, users_token, parameters_followers, PAGING_NAME, PAGING_KEY, REMAINING_KEY, RESET_EPOCH_KEY, addRelationToResults, {200 : 'ok', 401 : 'ok', 429 : 'wait'})
    current_function.run()
    logger.info('tw_extraction post_followers')

    '''
    if (force_stop is True):
        return
    '''

    """Extract Following ids"""
    url = 'https://api.twitter.com/1.1/friends/ids.json'
    #current_function = ApiLimitFunction(url, CONSUMER, TOKENS, parameters_friends, PAGING_NAME, PAGING_KEY, REMAINING_KEY, RESET_EPOCH_KEY, addRelationToResults, {200 : 'ok', 401 : 'ok', 429 : 'wait'})
    current_function = ApiLimitFunction(url, app_token, users_token, parameters_friends, PAGING_NAME, PAGING_KEY, REMAINING_KEY, RESET_EPOCH_KEY, addRelationToResults, {200 : 'ok', 401 : 'ok', 429 : 'wait'})
    current_function.run()
    logger.info('tw_extraction post_friends')

    '''
    if (force_stop is True):
        return
    '''

    """Extract Follower & Following"""
    url = 'https://api.twitter.com/1.1/users/lookup.json'
    parameters = get_hundred_ids()
    #current_function = ApiLimitFunction(url, CONSUMER, TOKENS, parameters, None, None, REMAINING_KEY, RESET_EPOCH_KEY, addAllUsersToResults, {200 : 'ok', 401 : 'ok', 429 : 'wait'})
    current_function = ApiLimitFunction(url, app_token, users_token, parameters, None, None, REMAINING_KEY, RESET_EPOCH_KEY, addAllUsersToResults, {200 : 'ok', 401 : 'ok', 429 : 'wait'})
    current_function.run()
    logger.info('tw_extraction post_lookup')

