from __future__ import absolute_import

import time
from threading import Timer
import logging

import requests
from requests_oauthlib import OAuth1

#logging.config.fileConfig('logging.conf')

logger = logging.getLogger('core')

"""
class ApiLimitFunctionDict(dict):
    """"""
    The dictionary just died because there is a while loop in the function
    so that the second api function will not be executed before the other
    ends.
    This class inherits from dictionary base class.
    >> addApiFunction a new function to run also takes a list of connections
    that creates a new TwitterApiLimitFunction.
    >> run() runs a for loop for all TwitterApiLimitFunction in the dict.
    """"""

    def addApiFunction(self, api_function, list_connections, delegate):
        # Creer la classe TwitterApiLimitParameters
        # Fixer les parametres connection et api_function
        self[api_function] = TwitterApiFunction(api_function, list_connections, delegate)

    def appendParameters(self, api_function, parameters):
        self[api_function].append(parameters)

    def run(self, list_connections):
        for api_function in self:
            self[api_functt_______ion].start()
    """

class DataExtractionException(Exception):
    def __init__(self, url, msg, status_code):
        self.url = url
        self.msg = msg
        self.status_code = status_code
    
    def __str__(self):
        return self.url + " " + self.msg + str(self.status_code)


class ApiLimitFunction(object):
    """
    This class executes the api call for all the parameters using
    all the connections available.
    """

    #def __init__(self, pathToBaseFolder, _delegateStoreJson):
    #"""
    #This function takes as an input the base folder then adds the api name to extract:
    #- The list of connections to be used for the extraction
    #- The list of parameters to extract
    #"""
    #self.all_conn = get from files
    #self.all_parameters = get from files
    #self.paging_key = get from files
    #self.delegate = _delegate
    
    def __init__(self, url, consumer, tokens, parameters, paging_name, paging_key,
                    remaining_key, reset_epoch_key, _delegateStoreJson, status_codes = {200 : 'ok'}):
        """
        - url: Complete url to the Api
        - consumer: Dictionary {'key' : 'key_value', 'secret' : 'secret_value'}
        - tokens: Dictionary list [{'key' : 'key_value1', 'secret' : 'secret_value1'}, 
            {'key' : 'key_value2', 'secret' : 'secret_value2'}]
        - parameters: Dictionary list [{'parameter_key1' : 'parameter_key1_value1', 'parameter_key2' : 'parameter_key2_value1'}, 
            {'parameter_key1' : 'parameter_key1_value2', 'parameter_key2' : 'parameter_key2_value2'}]
        - paging_name: string name for the paging parameter, typically 'cursor'
        - paging_key: string for getting the next paging value, typically 'next_cursor'
        - remaining_key: string, typically 'x-rate-limit-remaining'
        - reset_epoch_key: string, typically 'x-rate-limit-reset'
        - _delegateStoreJson: Delegate to the storing function
        - status_codes: Dictionary telling the algorithm to keep going when status code is ok (typically 200),
        getResetEpoch when status code is not Ok (typically 429). The rest of the codes will enable a loop
        """
        logger.debug('ApiLimitFunction.init: url %s - parameters %s', url, parameters)

        self.dgStoreJson = _delegateStoreJson
        self.parameters = parameters
        self.connections = []
        self.paging_name = paging_name
        self.status_codes = status_codes
        self.force_stop = False

        for token in tokens:
            oauth = OAuth1(consumer['key'], consumer['secret'], token['key'],token['secret'], signature_type='auth_header')
            conn = ApiLimitConnection(url, oauth, paging_key, remaining_key, reset_epoch_key, status_codes)
            self.connections.append(conn)

    def run(self):
        """
        This function makes calls the API with parameters using all connections
        for performing the task.
        """
        logger.info('ApiLimitFunction.run: Start with parameters %s', len(self.parameters))
        logger.debug('ApiLimitFunction.run: parameters %s', self.parameters)

        # we check if there are some connections left every 10s
        while True:
            for connection in self.connections:
                try:
                    if (connection.available == True):
                        logger.info('ApiLimitFunction.run: Switching connection parameters %s',
                            len(self.parameters))
                        logger.debug('ApiLimitFunction.run: parameters %s', self.parameters)

                        remaining = 1

                        # Then we check if there are some parameters left
                        while ((remaining > 0) and (len(self.parameters) > 0)):
                            logger.debug('ApiLimitFunction.run while loop for parameters %s', len(self.parameters))

                            # Call the api with connection and self.all_parameters[0]
                            status_code = connection.callApi(self.parameters[0])
                            
                            # Get the action associated to this code, default is loop
                            status_action = self.status_codes.get(status_code, 'loop')

                            # Normal case
                            if (status_action is 'ok'):
                                remaining = self._run_ok(connection, status_code)

                            # Rate limit case
                            elif (status_action is 'wait'):
                                remaining = self._run_wait(connection, status_code)

                            #Something went wrong in the connection so sleep & loop
                            else:
                                self._run_loop(connection, status_code)

                        if ( (len(self.parameters) == 0) or (self.force_stop is True) ):
                            logger.info('ApiLimitFunction.run No parameters left or force stop')
                            return;
                        else:
                            time.sleep(5)

                except DataExtractionException as e:
                    logger.exception('ApiLimitFunction.run parameters[0]: %s \nDataExtractionException %s', self.parameters[0], e)

    def _run_ok(self, connection, status_code):
        res_json = connection.getJson()
        remaining = connection.getRemaining()

        #call delegate function to store the json
        self.dgStoreJson(connection.url, self.parameters[0], status_code, res_json)

        # Update paging parameters for getting next results unless last result
        # Or delete the first parameter
        paging_value = connection.getPaging()

        if (paging_value is None or paging_value is 0):
            logger.debug('ApiLimitFunction.run DELETE parameter[0] %s', self.parameters[0])
            del(self.parameters[0])

        else:
            logger.debug('ApiLimitFunction.run update parameters %s for paging %s', 
            self.parameters[0], paging_value)
            self.parameters[0][self.paging_name] = paging_value

        #Let the server breath
        time.sleep(1)

        logger.info('ApiLimitFunction.run %s parameters left', len(self.parameters))

        return remaining

    def _run_wait(self, connection, status_code):
        logger.critical('ApiLimitFunction.run status_code: %s for parameters: %s, GetResetEpoch & wait', 
            status_code, self.parameters[0])

        remaining = 0
        reset_epoch = connection.getResetEpoch()
        connection.setFire(reset_epoch)

        return remaining

    def _run_loop(self, connection, status_code):
        logger.critical('ApiLimitFunction.run status_code: %s for parameters: %s, Sleeping 10s', 
            status_code, self.parameters[0])

        time.sleep(10)

    def stop(self):
        logger.critical('ApiLimitFunction._run_stop received')
        
        self.force_stop = True

        for connection in self.connections:
            connection.cancelTimer()

        logger.critical('ApiLimitFunction._run_stop complete') 


class ApiLimitConnection(object):
    """
    This class stores one function connection to the API and manages its scheduler.
    """

    def __init__(self, url, oauth, paging_key, remaining_key, reset_epoch_key, status_codes):
        """
        This function initiates the class with url, Oauth permissions, paging key
        for accessing next pages of results (if required), and a delegate to the
        function for storing the results.
        """
        logger.debug('ApiLimitConnection.init url %s', url)
        
        self.url = url
        self.oauth = oauth
        self.paging_key = paging_key
        self.remaining_key = remaining_key
        self.reset_epoch_key = reset_epoch_key
        self.status_codes = status_codes

        self.available = True
        self.request = None
        self.timer = None

    def getJson(self):
        """
        This function returns the Json when the status code is 200
        """

        res_json = None

        status_action = self.status_codes.get(self.request.status_code, 'loop')

        if (status_action is 'ok'):
            res_json = self.request.json()
        else:
            logger.critical('ApiLimitConnection.getJson url %s - status code %s \nrequest %s',
                self.url, self.request.status_code, self.request)
            raise DataExtractionException(self.url, "Status code is not 200: ", self.request.status_code)

        '''
        if (self.request.status_code != 200 and self.request.status_code != 401) :
            logger.critical('ApiLimitConnection.getJson url %s - status code %s \nrequest %s',
                self.url, self.request.status_code, self.request)
            raise DataExtractionException(self.url, "Status code is not 200: ", self.request.status_code)
        else:
            res_json = self.request.json()
        '''

        logger.debug('ApiLimitConnection.getJson url %s', self.url)

        return res_json

    def getPaging(self):
        """
        This function returns the paging value when the status code is 200
        """

        status_action = self.status_codes.get(self.request.status_code, 'loop')

        if (status_action is not 'ok'):
            logger.critical('ApiLimitConnection.getPaging url %s - status code %s \nrequest %s',
                self.url, self.request.status_code, self.request)
            raise DataExtractionException(self.url, "Status code is not 200: ", self.request.status_code)

        '''
        if (self.request.status_code != 200):
            logger.critical('ApiLimitConnection.getPaging url %s - status code %s \nrequest %s',
                self.url, self.request.status_code, self.request)
            raise DataExtractionException(self.url, "Status code is not 200: ", self.request.status_code)
        '''

        if ((self.paging_key == None) or (self.request.status_code != 200)):
            paging_value = None
        else:
            paging_value = self.request.json()[self.paging_key]

        logger.debug('ApiLimitConnection.getPaging url %s - paging_key %s - paging_value %s', 
            self.url, self.paging_key, paging_value)

        return paging_value

    def getRemaining(self):
        """
        This function returns the remaining integer from the header
        """

        remaining = 0

        try:
            result = None

            if (self.request is not None):
                result = self.request.headers[self.remaining_key]

            if (result is not None):
                remaining = int(result)
            else:
                logger.critical('ApiLimitConnection.getRemaining url %s - request %s',
                    self.url, self.request.headers)
        except Exception as e:
            logger.exception('getRemaining')

        logger.debug('ApiLimitConnection.getRemaining url %s - remaining %s', 
            self.url, remaining)
        return remaining

    def getResetEpoch(self):
        """
        This function returns the reset_epoch from the header
        """

        reset_epoch = None
        result = None

        if (self.request != None):
            result = self.request.headers[self.reset_epoch_key]

        if (result is not None):
            reset_epoch = float(result)
        else:
            logger.critical('ApiLimitConnection.getResetEpoch url %s - request %s',
                self.url, self.request.headers)
            #wait 10 seconds
            reset_epoch = time.time() + 5

        logger.debug('ApiLimitConnection.getResetEpoch url %s - reset_epoch %s', 
            self.url, reset_epoch)
        return reset_epoch

    def fired(self):
        """
        When the scheduler fires, the connection becomes available
        """

        logger.info('ApiLimitConnection.fired url %s', self.url)

        self.available = True

    def callApi(self, parameters):
        """
        This function calls the API with the parameters, stores the retrieved Json and
        sets the timer to fire in reset_epoch - time.now seconds
        Returns -1 in case of failure
        """
        status_code = -1

        try:
            #Api Call
            self.request = requests.get(url=self.url, params=parameters, auth=self.oauth)
            status_code = self.request.status_code
            
            #if remaining = 0, the connection is not available then get the reset_epoch and schedule
            #if (headers['x-rate-limit-remaining'] == 0):
            if (self.getRemaining() is 0):
                logger.warning('ApiLimitConnection.callApi Remaining is 0 - url: %s - ResetEpoch: %s', self.url, self.getResetEpoch())
                self.setFire(self.getResetEpoch())

            logger.debug('ApiLimitConnection.callApi - url: %s - parameters: %s', self.url, parameters)

        except requests.exceptions.RequestException as e:
            logger.exception('ApiLimitFunction.run parameters[0]: %s \nrequests.exceptions.RequestException %s', parameters, e)

        except:
            logger.exception('callApi')
            #self.setFire(self.getResetEpoch())
            #status_code = 429

        return status_code

    def setFire(self, reset_epoch):
        """
        This function sets the timer to fire in reset_epoch - time.now seconds
        """

        #print "reset epoch:" + reset_epoch
        self.available = False
        # Check if header contains the specified key, then ...
        # Get the reset_epoch & seconds left before reset
        seconds_to_reset = reset_epoch - time.time()
        logger.debug('setFire - url %s - seconds to epoch: %s', self.url, seconds_to_reset)

        # program the timer to fire at the reset_epoch
        self.timer = Timer(seconds_to_reset, self.fired, ()).start()

    def cancelTimer(self):
        logger.warning('ApiLimitConnection.cancelTimer - url %s', self.url)
        
        if (self.timer != None):
            self.timer.cancel()
