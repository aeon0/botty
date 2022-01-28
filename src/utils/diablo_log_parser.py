import os
import numpy
from logger import Logger
from beautifultable import BeautifulTable

wkdir = os.getcwd()

#initialize strings
simple_string = ["Starting game", "Run Diablo", "ROF: Calibrated at WAYPOINT", "ROF: Calibrated at PENTAGRAM", "ROF: Teleporting directly to PENTAGRAM", "CS: OPEN TP", "CS: Calibrated at PENTAGRAM", "Checking Layout for Vizier", "Checking Layout for De Seis", "Checking Layout for Infector", "Waiting for Diablo to spawn", "End game", "Trying to chicken", "You have died"]
prefix_string = ["A1-L", "A2-Y", "B1-S", "B2-U", "C1-F", "C2-G"]
complex_string = ["Layout_check step 1/2", "Layout_check step 2/2", "Starting to clear Seal", "Boss: trying to open", "Fake: trying to open", "Kill Boss", "Attacking Vizier at position", "Attacking De Seis at position", "Attacking Infector at position", "Static Pathing to Pentagram", "Looping to Pentagram", "finished seal & calibrated at PENTAGRAM"]
error_string = ["End failed game"]
error_array = []
lines_before_error = 10
#initialize counter
simple_counter = numpy.zeros (len (simple_string)+1)
complex_counter = numpy.zeros ((len (prefix_string)+1, len (complex_string)+1))



#open file and gather information line by line
log_str = wkdir + "/info.log"
log_file = open (log_str, "r")
log_lines = log_file.readlines ()

line_counter = 0
for line in log_lines:
    #some temp values for looping
    simple_item_counter = 0
    prefix_counter = 0
    complex_item_counter = 0
    #check simple strings
    for string in simple_string: 
        if string in line:
            simple_counter [simple_item_counter] += 1
            break    
        simple_item_counter += 1
    #check concat strings
    for prefix in prefix_string:
        for string in complex_string:
            if ((prefix + "_" + string) in line):
                complex_counter [prefix_counter][complex_item_counter] += 1
                break
            complex_item_counter += 1
        prefix_counter += 1
    #check error strings
    for error in error_string:
        if error in line:
            error_array.append (log_lines [line_counter-lines_before_error:line_counter])
    line_counter += 1

log_file.close ()
#all lines checked create beatifultable
#some temp values for looping
simple_item_counter = 0
prefix_counter = 0
table1 = BeautifulTable ()
#append simple strings
for string in simple_string:
    table1.rows.append ([string, simple_counter [simple_item_counter]])
    simple_item_counter += 1

table2 = BeautifulTable ()
for prefix in prefix_string:
    complex_item_counter = 0
    for string in complex_string:
        table2.rows.append ([prefix + ': ' + string, complex_counter [prefix_counter, complex_item_counter]])
        complex_item_counter += 1
    prefix_counter += 1
table2.columns.header = ['String', 'amount']


result_file = open (wkdir + "/cs_result.txt", 'w')

result_file.write (str(table1))
result_file.write ("\n")
result_file.write (str(table2))

error_counter = 0
for error in error_array:
    error_counter += 1
    result_file.write (f"======================== current error_number {error_counter}\n")
    for line in error:
        Logger.info (line)
        result_file.write (line)

Logger.info ("=================================================================================================")
Logger.info ("Parsed info.log - results & details for failed runs stored in cs_result.txt in botty root folder")
Logger.info ("=================================================================================================")
Logger.info ("\n" + str(table1))



