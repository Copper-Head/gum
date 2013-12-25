# This program is free and subject to the conditions of the MIT license.
# If you care to read that, here's a link:
# http://opensource.org/licenses/MIT

# To-Do:
# line filtering in process_table_file

#===================== IMPORTS --- SETUP --- GLOBAL VARS ======================
import os
import sys
import re
from csv import DictReader, DictWriter
from collections import *
from itertools import *
from functools import *
from operator import *

#============================ Boolean Functions ===============================

def ID(anything):
    '''This function is mostly intended as a placeholder for functions that the
    user may want to pass.
    I am considering setting this to return the passed object instead of just
    True.'''
    return True

#============================ File I/O Functions ==============================

def list_to_plain_text(inputIter, newline='\n', itemType=str):
    '''Takes a iterable, adds a new line character to the end of each of its
    members and then returns a generator of the newly created items.
    The idea is to convert some sequence that was created with no concern for
    spliting it into lines into something that will produce a text file.
    It is assumed that the only input types will be sequences of lists or
    strings, because these are the only practically reasonable types to be
    written to files.
    It is also assumed that by default the sequence will consist of strings and
    that the lines will be separated by a Unix newline character.
    This behavior can be changed by passing different newline and/or itemType
    arguments.
    '''
    return (l+itemType(newline) for l in inputIter)

def proc_table_file(procType, func=None, *args, **kwargs):
    '''
    Optionally takes a procedure and its arguments and prepares them to be
    applied to a file.
    If proc is not given, simply returns a function that given a file name and
    formatting parameters returns a DictReader object.
    
    :type procType: string from {'map', 'reduce', 'filter'}
    :param procType: specifies what procedure to use; currently supports map
    and reduce
    :type func: function or None
    :param func: the function to be run through the file
    '''
    if func:
        func = partial(proc, *args, **kwargs)

    procs= {
            'map': imap,
            'filter': ifilter,
            'reduce': reduce
            }
    
    def open_table(fName, **fmtparams):
        '''Given name of file and some formatting parameters opens the file
        specified by the name as a DictReader object with the passed formatting
        parameters.
        
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
        #first we open the file and create a DictReader object
        with open(fName, 'rU') as f:
            readIn = DictReader(f, **fmtparams)
        if not func:
            return readIn
        return procs[procType](func, readIn)
    
    return open_table

def imap_table_file(func=None, *args, **kwargs):
    return proc_table_file('map', func, *args, **kwargs)

def reduce_table_file(func=None, *args, **kwargs):
    return proc_table_file('reduce', func, *args, **kwargs)

def unprocessed_csv(fName, **fmtparams):
    return imap_table_file()(fName, **fmtparams)

def proc_dir(procType, func, *args, **kwargs):
    '''
    Takes a procedure and its arguments and prepares them to be
    applied to a file.
    If proc is not given, simply returns a function that given a file name and
    formatting parameters returns a DictReader object.
    
    :type procType: string from {'map', 'reduce', 'filter'}
    :param procType: specifies what procedure to use; currently supports map
    and reduce
    :type func: function or None
    :param func: the function to be run through the file
    '''
    partial_func = partial(proc, *args, **kwargs)

    procs= {
            'map': imap,
            'filter': ifilter,
            'reduce': reduce
            }
    
    def open_dir(dirName, filterfunc=None):
        '''This function applies partial_func from the enclosing environment
        to all the files in a directory that satisfy the conditions specified 
        in 'filterfunc'.
        The latter is by default None, which returns all files in the directory.

        :type dirName: string
        :param dirName: name of directory
        :type filterfunc: function from strings (file names) to truth values
        :param filterfunc: filtering criteria for file names
        '''
        filtered = ifilter(filterfunc, iter(os.listdir(dirName)))
        paths = (os.path.join(dirName, fName) for fName in filtered)
        return procs[procType](partial_func, paths)

    return open_dir

def imap_dir(func, *args, **kwargs):
    return proc_dir('map', func, *args, **kwargs)

def reduce_dir(func, *args, **kwargs):
    return proc_dir('reduce', func, *args, **kwargs)

def write_to_csv(fName, data, header, **kwargs):
    '''Writes data to file specified by filename. 
    
    :type fName: string
    :param fName: name of the file to be created
    :type data: iterable
    :param data: some iterable of dictionaries each of which must not contain keys 
    absent in the 'header' argument
    :type header: list
    :param header: list of columns to appear in the output
    :type **kwargs: dict
    :param **kwargs: parameters to be passed to DictWriter.
    For instance, restvals specifies what to set empty cells to by default or
    'dialect' loads a whole host of parameters associated with a certain csv
    dialect (eg. "excel").
    '''
    with open(fName, 'w') as f:
        output = DictWriter(f, header, **kwargs)
        output.writeheader()
        output.writerows(data)

def write_to_txt(fName, data, addNewLines=False, **kwargs):
    '''Writes data to a text file.
    
    :type fName: string
    :param fName: name of the file to be created
    :type data: iterable
    :param data: some iterable of strings or lists of strings
    :type addNewLines: bool
    :param addNewLines: determines if it's necessary to add newline chars to
    members of list
    :type kwargs: dict
    :param kwargs: key word args to be passed to list_to_plain_text, if needed
    '''
    if addNewLines:
        data = list_to_plain_text(data, **kwargs)
    with open(fName, 'w') as f:
        f.writelines(data)

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

