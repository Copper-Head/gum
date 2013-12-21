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
    '''This function is mostly intended as a placeholder for functions that the
    user may want to pass.
    I am considering setting this to return the passed object instead of just
    True.'''
    return True

#============================ File I/O Functions ==============================

def process_dir(dirName, proc=None, filterfunc=ID, data=[], delim='\t', **misc):
    '''This is very primitive, will need to improve somewhat...'''
    for fName in os.listdir(dirName):
        if filterfunc(fName):
            data = process_csv(os.path.join(dirName, fName), proc, data,
                    delim=delim, fname=fName, **misc)
    return data

def process_table(fName, **fmtparams):
    '''Given name of file and some formatting parameters opens the
    corresponding file and prepares it for processing.
    Returns a functor that expects some sort of procedure to run on the file.
    
    Intended as a generic wrapper for opening a file and converting it to a
    csv.DictReader object, then processing it in some way.
    It is assumed that the file being processed is a parseable table with
    values split up into columns separated by either whitespace or commas.
    The formatting parameters are left unspecified on purpose, here are some
    examples:
    - fieldnames -> define your own header for the output 
    - delimiter -> ',' or '\t'
    - dialect 
    One can also read up on them here:
    http://docs.python.org/2/library/csv.html#csv-fmt-params

    :type fName: string
    :param fName: name of file to be processed
    :type fmtparams: dict
    :param fmtparams: parameters used by DictReader to open files

    '''
    if 'fieldnames' in misc:
        fields = misc['fieldnames']
    else:
        fields = None

    with open(fName, 'rU') as f:
        readIn = DictReader(f, **fmtparams)

    def waiting_for_proc(proc=None, *misc, **kwmisc):
        '''Wrapper function for other functions (the proc argument).
        If proc is not given, simply returns a list of the lines in the file as
        dictionaries of column_name:column_value.
        If proc is provided it is run on every line in the file along with
        whatever arguments that procedure requires.'''
        if proc:
            for line in readIn:
                data = proc(line, *misc, **kwmisc)
        else:
            return list(readIn)
        return data

    return waiting_for_proc

def write_to_csv(fName, data, header, **kwargs):
    '''Writes data to file specified by filename. 
    :type fName: string
    :param fName: name of the file to be created
    :type data: list
    :param data: list of dictionaries with no keys absent in the header list
    :type header: list
    :param header: list of columns to appear in the output
    :type **kwargs: dict
    :param **kwargs: some parameters to be passed to DictWriter.
    For instance, restvals specifies what to set empty cells to by default.
    '''
    with open(fName, 'w') as f:
        output = DictWriter(f, header, **kwargs)
        output.writeheader()
        output.writerows(data)

#============================ Data Manipulation Functions =====================

def find_something(smthng, string, All=False):
    '''I'm not sure I should keep this'''
    regex = re.compile(smthng)
    if All:
        return regex.findall(string)
    return regex.findall(string)[0]

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

