#!/usr/bin/env python

import os
import sys
import sqlite3
import socket
import hashlib
import logging
import time
from collections import namedtuple

from sickle import Sickle # pip install sickle
import requests # pip install requests

ENV = namedtuple('ENV_', ['ACCESS_TOKEN', 'ZENODO_DB', 'LOG', 
                         'ZENODO_OAI', 'SOCKET_NAME'])  

def get_environ():
    """ Return environmental variables in the ENV namedtuple """
    def get_(var):
        try: 
            VAR = os.environ[var]
        except KeyError:
            print("environmental varible {} not found".format(var))
            sys.exit(1)
        return VAR

    # get the ACCESS_TOKEN from https://goo.gl/7HXLUK 
    ENV.ACCESS_TOKEN = get_('ACCESS_TOKEN')
    ENV.ZENODO_OAI = get_('ZENODO_OAI')
    ENV.ZENODO_DB = get_('ZENODO_DB')
    ENV.SOCKET_NAME = get_('SOCKET_NAME')
    
    # if LOG not exist then use the stderr  
    try:
        ENV.LOG = os.environ['LOG']
    except:
        ENV.LOG = sys.stderr

# source https://goo.gl/sOKz1b 
def get_logger(level=logging.WARNING):
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=ENV.LOG, format=FORMAT, level=level)


# source https://goo.gl/kvLfCS
def get_lock(process_name):
    """Prevent multiple processes running at the same time
                  ***it will work only in linux***
    """
    # Without holding a reference to our socket somewhere it gets garbage
    # collected when the function exits
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    
    try:
        get_lock._lock_socket.bind('\0' + process_name)
        #print('locked')
        logging.info('%s started', process_name)
    
    except socket.error:
        logging.info('%s already running', process_name)
        sys.exit()


def main():
    '''
    '''
    # collect info and block the proccess ..  
    get_environ()
    get_logger(level=logging.DEBUG)
    get_lock(ENV.SOCKET_NAME)
   
    # get the sqlite3 database 
    conn = sqlite3.connect(ENV.ZENODO_DB)
    c = conn.cursor()
    try:
        c.execute('''
                CREATE TABLE zenodo (
                   --- from the oai2d api
                   creator    text, 
                   doi        text,
    
                   --- from the rest api
                   creation_date text,
                   link          text,
                   checksum      text,
    
                   --- other stuff
                   dfile      text, -- downloaded file renamed to 
                   downloaded text,
                   evaluated  text,
                   
                   UNIQUE(doi))
                ''')
    except (sqlite3.IntegrityError, sqlite3.OperationalError):
        pass

    # harvest zenodo with oai 
    sickle = Sickle(ENV.ZENODO_OAI)
    records = sickle.ListRecords(metadataPrefix='oai_dc')
    
    for f in records:
        # check if the doi record has been processed
        try:
            creator = f.metadata['creator'][0]
            doi = f.metadata['identifier'][1]
            conceptrecid = doi.split('.')[2]
            c.execute('SELECT doi, downloaded FROM zenodo WHERE doi=="{}"'.format(doi))
            doi, downloaded = c.fetchall()[0] # this will raise an exception if no data 
            if doi and downloaded == 'y':
                logging.info('doi = {} already downloaded'.format(doi))
                #logging.info(' : doi = %s already downloaded', doi)
                #logging.warning('using the input text for training!')
                continue
    
        except IndexError: # the doi doesn't exist
            pass 
         
        try:
    
            # get the information from the REST api
            url_info = "https://zenodo.org/api/deposit/depositions/"
            url_info+= "{}?access_token={}".format(conceptrecid, ENV.ACCESS_TOKEN)
            r = requests.get(url_info)
            res_json = r.json() # if error????
            
            # valid for api v?
            creation_date = res_json['created']
            link = res_json['files'][0]['links']['download']
            checksum = res_json['files'][0]['checksum'] 
            logging.info('getting {} doi'.format(doi))
    
            # download file and compute its checksum 
            r = requests.get(link, params={'access_token': ENV.ACCESS_TOKEN})
            md5_content = hashlib.md5(r.content).hexdigest()
    
            # check if the file is not corrupt  
            if md5_content == checksum:
                dfile = "downloaded/{}".format(conceptrecid)
                with open(dfile, "wb") as d_file:
                    d_file.write(r.content)
                downloaded = 'y'
                logging.info('{} passed md5sum test'.format(dfile))
            else: # ummm then there is a problem with the connection?
                logging.warning('{} md5sum mismatch'.format(dfile)) 
                downloaded = 'n'
            evaluated = 'n'

            c.execute('''INSERT INTO zenodo 
                         VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}");
                         '''.format(creator, doi, creation_date, link, 
                                    checksum, dfile, downloaded, evaluated))
            
        except sqlite3.IntegrityError: # tried to insert something that already
            pass
   
    # save the data in the database 
    conn.commit()
    conn.close()
    #time.sleep(200)

    logging.info('finished process')


if __name__ == '__main__':
    main()




