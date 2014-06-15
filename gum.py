# This program is free and subject to the conditions of the MIT license.
# If you care to read that, here's a link:
# http://opensource.org/licenses/MIT

# To-Do:
# some automation of text file writing: functions to write to files with
# new-lines or commas
# some more general purpose function to create filenames with dates
# currently that's hidden inside the log creation function, but can be useful
# for other filename generation tasks as well.

#===================== IMPORTS --- SETUP --- GLOBAL VARS ======================
import os
import re
import logging
import cPickle

import csv
from time import localtime


#============================ File I/O Functions ==============================


def gen_file_paths(dir_name, filter_func=None):
    '''A function for wrapping all the os.path commands involved in listing files
    in a directory, then turning file names into file paths by concatenating
    them with the directory name.
    This also optionally supports filtering file names using filter_func.
    '''
    if filter_func:
        just_file_names = filter(filter_func, os.listdir(dir_name))
    else:
        just_file_names = os.listdir(dir_name)
    
    return (os.path.join(dir_name, file_name) for file_name in just_file_names)


def read_table(file_name, function=None, **fmtparams):
    ''' Function that simplifies reading it table files of any kind.'''
    with open(file_name) as opened_file:
        # if user hasn't defined a dialect, try to sniff it out
        if 'dialect' not in fmtparams:
            fmtparams['dialect'] = csv.Sniffer().sniff(opened_file.read(1024))
            # this line resets the file object to its beginning
            opened_file.seek(0)
        # check if passed file has a header
        detect_header = csv.Sniffer().has_header(opened_file.read(1024))
        opened_file.seek(0)
        # if column names were explicitly passed or header was detected...
        if 'fieldnames' in fmtparams or detect_header:
            # ,,, use Dictreader 
            reader = csv.DictReader(opened_file, **fmtparams)
        else:
            # otherwise create a simple reader
            reader = csv.reader(opened_file, **fmtparams)
        # if user passed function, give it the reader object for processing
        if function:
            return function(reader)
        # otherwise turn reader into tuple, otherwise the file gets closed 
        # preventing further processing
        return tuple(reader)


################################################################################
## Writing to files
################################################################################

def create_row_dicts(fields, data, fill_val='NA'):
    '''Helper generator function for the write_to_table(). Collecting data
    is often much more efficient and clear when this data is stored in tuples
    or lists, not dictionaries.
    Python's csv DictWriter class requires that it be passed a sequence of 
    dictionaries, however.
    This function takes a header list of column names as well as some data in
    the form of a sequence of rows (which can be tuples or lists) and converts
    every row in the data to a dictionary usable by DictWriter.
    '''
    for row in data:
        length_difference = len(fields) - len(row)
        error_message = 'There are more rows than labels for them: {0}'
        if length_difference < 0:
            print('Here are the column labels', fields)
            print('Here are the rows', row)
            raise Exception(error_message.format(length_difference))
        elif length_difference > 0:
            row = row + (fill_val,) * length_difference
        yield dict(zip(fields, row))


def write_to_table(file_name, data, header=None, **kwargs):
    '''Writes data to file specified by filename.

    :type file_name: string
    :param file_name: name of the file to be created
    :type data: iterable
    :param data: some iterable of dictionaries each of which
    must not contain keys absent in the 'header' argument
    :type header: list
    :param header: list of columns to appear in the output
    :type **kwargs: dict
    :param **kwargs: parameters to be passed to DictWriter.
    For instance, restvals specifies what to set empty cells to by default or
    'dialect' loads a whole host of parameters associated with a certain csv
    dialect (eg. "excel").
    '''
    with open(file_name, 'w') as f:
        if header:
            output = csv.DictWriter(f, header, **kwargs)
            output.writeheader()
            data = create_row_dicts(header, data, fill_val=output.restval)
        else:
            output = csv.writer(f, **kwargs)
        output.writerows(data)


def write_to_txt(file_name, data, mode='w', AddNewLines=False, **kwargs):
    '''Writes data to a text file.

    :type fName: string
    :param fName: name of the file to be created
    :type data: iterable
    :param data: some iterable of strings or lists of strings (not a string)
    :type addNewLines: bool
    :param addNewLines: determines if it's necessary to add newline chars to
    members of list
    :type kwargs: dict
    :param kwargs: key word args to be passed to list_to_plain_text, if needed
    '''
    if AddNewLines:
        data = add_newlines(data, **kwargs)
    with open(file_name, mode=mode) as f:
        f.writelines(data)


#-------------------------- Logging and Pickling ------------------------------

def create_debug_log(base='error', ext='.log', separator='_', app='DEFAULT'):
    '''wrapper for creating a logger.

    :type base: string
    :param fileNameBase: base for the log file name to which date, time,
    and the extension are later attached.
    :type ext: string
    :param ext: string for an extension
    :type separator: string
    :param separator: character used to separate different parts of the
    filename
    :type app: string
    :param app: name for the application that generates the error
    '''
    #sanity-checking the extension
    if not ext.startswith('.'):
        ext = '.' + ext

    date = localtime()
    #create log file name
    errorFile = '_'.join([str(date.tm_year),
                          str(date.tm_mon),
                          str(date.tm_mday),
                          str(date.tm_hour),
                          str(date.tm_min),
                          base + ext])
    logging.basicConfig(filename=errorFile, level=logging.DEBUG)
    return logging.getLogger(app)


def pickle_data(data, file_name, ext='.picl'):
    '''wrapper for picling any data.
    :type data: any
    :param data: python object to be pickled
    :type fileName: string
    :param fileName: specifies the name of the pickled file
    :type ext: string
    :param ext: adds and extension to the file name
    '''
    #sanity-checking the extension
    if not ext.startswith('.'):
        ext = '.' + ext

    with open(file_name + ext, 'w') as f:
        cPickle.dump(corpus, f)


#============================ Data Manipulation Functions =====================

def add_newlines(input_iter, newline='\n', item_type=str):
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
    return (l + item_type(newline) for l in input_iter)


def newline_list(input_list):
    return add_newlines(input_list, item_type=list)


def find_something(smthng, string, All=False):
    '''I'm not sure I should keep this'''
    regex = re.compile(smthng)
    if All:
        return regex.findall(string)
    return regex.findall(string)[0]


def subset_dict(src_dict, relevants, replace=False, exclude=False):
    '''Given some keys and a dictionary returns a dictionary with only
    specified keys. Assumes the keys are in fact present and will raise an
    error if this is not the case'''
    '''Think about ways to make chains of maps: A > B + B > C turns into A >
    C'''
    if replace:
        return dict((relevants[x], src_dict[x]) for x in relevants)
    if exclude:
        try:
            return dict((x, src_dict[x]) for x in src_dict
                        if x not in relevants)
        except Exception as e:
            print 'Unable to process this: ', src_dict
            raise
    try:
        return dict((x, src_dict[x]) for x in relevants)
    except Exception as e:
        print 'Unable to process this: ', src_dict
        raise e


#================================ Statistics ===================================

def mean(iterable):
    # just in case we got passed an iterator, not a list
    safety = tuple(iterable)
    return len(safety) / sum(safety)


def median(iterable):
    # just in case...
    safety = tuple(iterable)
    sorted_safety = sorted(safety)
    length = len(safety)
    middle = length / 2
    if length % 2 != 0:
        return sorted_safety[middle]
    else:
        return (sorted_safety[middle] + sorted_safety[middle - 1]) / 2


#================================= __MAIN__ ===================================

def main():
    pass


#------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
