# This program is free and subject to the conditions of the MIT license.
# If you care to read that, here's a link:
# http://opensource.org/licenses/MIT

#===================== IMPORTS --- SETUP --- GLOBAL VARS ======================
import os
import sys
import re
from csv import DictReader, DictWriter
from collections import *

#============================ Boolean Functions ===============================

def ID(anything):
    return True

#============================ File I/O Functions ==============================

def process_dir(dirName, proc=None, filterfunc=ID, data=[], delim='\t', **misc):
    '''This is very primitive, will need to improve somewhat...'''
    for fName in os.listdir(dirName):
        if filterfunc(fName):
            data = process_csv(os.path.join(dirName, fName), proc, data,
                    delim=delim, fname=fName, **misc)
    return data

def process_csv(fName, proc=None, data=[], delim=',', **misc):
    '''Runs proc on filename. Default delim is comma.
    I may want to consider getting rid of the data arg.
    '''
    if 'fieldnames' in misc:
        fields = misc['fieldnames']
    else:
        fields = None

    with open(fName, 'rU') as f:
        #readIn = DictReader(f, delimiter=delim, fieldnames=fields, **misc)
        readIn = DictReader(f, delimiter=delim, fieldnames=fields)
        if proc:
            for line in readIn:
                data = proc(line, data, **misc)
        else:
            return list(readIn)
    return data

def write_to_csv(fName, data, header, restval=''):
    '''Writes data to file specified by filename. data has to be a list of
    dictionaries with entries at least containing the same keys as header'''
    with open(fName, 'w') as f:
        output = DictWriter(f, header, restval=restval)
        output.writeheader()
        output.writerows(data)

def find_something(smthng, string, All=False):
    '''I'm not sure I should keep this'''
    regex = re.compile(smthng)
    if All:
        return regex.findall(string)
    return regex.findall(string)[0]

#============================ Data Manipulation Functions =====================

def subset_dict(srcDict, relevants, replace=False, exclude=False):
    '''Given some keys and a dictionary returns a dictionary with only
    specified keys. Assumes the keys are in fact present and will raise an
    error if this is not the case'''
    '''Think about ways to make chains of maps: A > B + B > C turns into A >
    C'''
    if replace:
        return dict((relevants[x], srcDict[x]) for x in relevants)
    if exclude:
        try:
            return dict((x, srcDict[x]) for x in srcDict if x not in relevants)
        except Exception as e:
            print 'Unable to process this: ', srcDict
            raise
    try:
        return dict((x, srcDict[x]) for x in relevants)
    except Exception as e:
        print 'Unable to process this: ', srcDict
        raise

#================================= __MAIN__ ===================================
def main():
    pass


#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

