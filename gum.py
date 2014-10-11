'''Gum, a swiss-army-knife module.'''

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

    :param dir_name: name of directory to list files in
    :type dir_name: string
    :param filter_func: optional name of function to filter file names by
    :type filter_func: None by default, function if passed
    :returns: list of paths for files in *dir_name*
    '''
    gen_full_path = lambda f_name: os.path.join(dir_name, f_name)
    file_paths = map(gen_full_path, os.listdir(dir_name))

    if filter_func:
        return filter(filter_func, file_paths)

    return file_paths


def read_table(file_name, processor=None, *args, **fmtparams):
    ''' Function that simplifies reading table files of any kind.

    Optionally takes a function that processes the csv while it's open.

    :param file_name: name of the table file to open
    :type file_name: string
    :param processor: (optional) a function to process the table file
    :type processor: None (default) or function
    :fmtparams: formatting parameters for **csv.Dictreader** or **csv.reader**
    :returns: tuple sequence of lines or result of *processor*
    '''
    with open(file_name) as opened_file:
        if 'fieldnames' in fmtparams:
            print 'Using csv.DictReader because a header was passed.'
            reader = csv.DictReader(opened_file, **fmtparams)
        else:
            # otherwise create a simple reader
            print 'No header specified, using smple reader.'
            reader = csv.reader(opened_file, **fmtparams)
        # if user passed function, give it the reader object for processing
        if processor:
            print 'using funtion'
            return processor(reader, *args)
        # otherwise turn reader into tuple, because file gets closed 
        # upon exiting this function which prevents further processing
        # 
        # Note: Disabling Excel logic till it's tested
        # if reader.dialect == 'excel':
        #     # converting DictReader to tuple requires dropping first row
        #     print 'Converting Excel file "{0}" to tuple...'.format(file_name)
        #     return tuple(reader)[1:]
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

    :param fields: a tuple of list of column labels
    :type fields: iterable
    :param data: sequence of rows to be turned into dictionaries
    :type data: iterable
    :param fill_val: (optional) specifies what to fill empty fields with
    :type fill_val: string
    :yields: a dict usable by **csv.DictWriter**
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
    :param data: data we want to write to file
    :type header: tuple or list
    :param header: sequences of columns to appear in the output
    :type kwargs: dictionary
    :param kwargs: parameters to be passed to DictWriter
    :returns: Nothing, just writes *data* to file
    '''
    with open(file_name, 'w') as f:
        if header:
            output = csv.DictWriter(f, header, **kwargs)
            output.writeheader()
            data = create_row_dicts(header, data, fill_val=output.restval)
        else:
            output = csv.writer(f, **kwargs)
        output.writerows(data)


def write_to_txt(file_name, data, mode='w', newline='\n'):
    '''Writes data to a text file.

    :type fName: string
    :param fName: name of the file to be created
    :type data: iterable
    :param data: some iterable of strings or lists of strings (not a string)
    :param mode: (optional) can be changed to "a" to append instead of overwriting
    :type mode: string
    :param newline: specifies new line character to add
    :type newline: string (default), can be anything
    '''
    add_newlines = (line + newline for line in data)
    with open(file_name, mode=mode) as f:
        f.writelines(add_newlines)


#-------------------------- Logging and Pickling ------------------------------

def create_debug_log(base='error', ext='.log', separator='_', app='DEFAULT'):
    '''This is a wrapper for creating a logger.

    :type base: string
    :param base: base for the log file name (default = "error")
    :type ext: string
    :param ext: (optionally) user-defined file extension
    :type separator: string
    :param separator: character used to separate different parts of the file name
    :type app: string
    :param app: name for the application that generates the error
    :returns: instance of **logging.getLogger()**
    '''
    #sanity-checking the extension
    if not ext.startswith('.'):
        ext = '.' + ext

    date = localtime()
    #create log file name
    error_file_name = '_'.join([str(date.tm_year),
                          str(date.tm_mon),
                          str(date.tm_mday),
                          str(date.tm_hour),
                          str(date.tm_min),
                          base + ext])
    logging.basicConfig(filename=error_file_name, level=logging.DEBUG)
    return logging.getLogger(app)


def pickle_data(data, file_name, ext='.picl'):
    '''This is a wrapper for pickling any data.

    :type data: any
    :param data: python object to be pickled
    :type fileName: string
    :param fileName: specifies the name of the pickled file
    :type ext: string
    :param ext: adds and extension to the file name
    :returns: Nothing, writes *data* to file
    '''
    #sanity-checking the extension
    if not ext.startswith('.'):
        ext = '.' + ext

    with open(file_name + ext, 'w') as f:
        cPickle.dump(corpus, f)


#============================ Data Manipulation Functions =====================

# def add_newlines(input_iter, newline='\n', item_type=str):
#     '''Takes a iterable, adds a new line character to the end of each of its
#     members and then returns a generator of the newly created items.
#     The idea is to convert some sequence that was created with no concern for
#     spliting it into lines into something that will produce a text file.
#     It is assumed that the only input types will be sequences of lists or
#     strings, because these are the only practically reasonable types to be
#     written to files.
#     It is also assumed that by default the sequence will consist of strings and
#     that the lines will be separated by a Unix newline character.
#     This behavior can be changed by passing different newline and/or itemType
#     arguments.
#     '''
#     return (l + item_type(newline) for l in input_iter)


# def newline_list(input_list):
#     return add_newlines(input_list, item_type=list)


# def find_something(smthng, string, All=False):
#     '''I'm not sure I should keep this'''
#     regex = re.compile(smthng)
#     if All:
#         return regex.findall(string)
#     return regex.findall(string)[0]


# def subset_dict(src_dict, relevants, replace=False, exclude=False):
#     '''Given some keys and a dictionary returns a dictionary with only
#     specified keys. Assumes the keys are in fact present and will raise an
#     error if this is not the case'''
#     '''Think about ways to make chains of maps: A > B + B > C turns into A >
#     C'''
#     if replace:
#         return dict((relevants[x], src_dict[x]) for x in relevants)
#     if exclude:
#         try:
#             return dict((x, src_dict[x]) for x in src_dict
#                         if x not in relevants)
#         except Exception as e:
#             print 'Unable to process this: ', src_dict
#             raise
#     try:
#         return dict((x, src_dict[x]) for x in relevants)
#     except Exception as e:
#         print 'Unable to process this: ', src_dict
#         raise e


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
