from __future__ import absolute_import

from datetime import datetime
import logging

from django.conf import settings

import pymongo
from pymongo import MongoClient


logger = logging.getLogger('core')

def get_collection(database, collection):
    logger.debug('get collection %s from database %s', collection, database)

    client = MongoClient(settings.MONGO_CLIENT)
    db = client[database]

    logger.debug('return database %s collection %s', database, collection)

    return db[collection]

def drop_collection(database, collection):
    logger.debug('Drop collection %s', database)

    client = MongoClient(settings.MONGO_CLIENT)
    db = client[database]
    db.drop_collection(collection)


def add_dt_to_mongo(database, collection, date_fields):
    logger.debug('add_dt_to_mongo')

    try:
        #db_name = __package__.replace('.', '_')
        collection = get_collection(database, collection)

        for doc in collection.find():
            for datefield in date_fields:
                doc['dt_' + datefield] = get_dt( doc[ datefield ] )
            collection.replace_one({'_id': doc['_id']}, doc)

    except Exception as e:
        logger.exception(e)

def add_dt_to_json(the_json, date_fields):
    logger.debug('add_dt_to_json')

    try:
        for datefield in date_fields:
            the_json['dt_' + datefield] = get_dt( the_json[ datefield ] )
        return the_json

    except Exception as e:
        logger.exception(e)


def get_dt(date_val):
    dt_val = datetime.fromtimestamp(0)
    try:
        if (date_val is not None):
            dt_val = datetime.strptime(date_val, '%a %b %d %H:%M:%S %z %Y')
    except Exception as e:
        logger.exception(e)
    return dt_val
