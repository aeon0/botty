import os
import numpy
from logger import Logger
from beautifultable import BeautifulTable

wkdir = os.getcwd()

#"Entrance 1 Layout_check step 1/2:", "Entrance 1 Layout_check step 2/2:", "Entrance 1 Layout_check step 1/2:", "Entrance 1 Layout_check step 2/2:", "Entrance 2 Layout_check step 2/2: Failed to determine", "Entrance 2 Layout_check step 2/2: Failed to determine", "CS Entrance Style 1", "CS Entrance Style 2", " - cleaning hall 1/3", " - cleaning hall 2/3", " - cleaning hall 3/3",

#initialize strings
simple_string = ["Starting game", "Run Diablo", "ROF: Calibrated at WAYPOINT", "ROF: Calibrated at CS ENTRANCE","CS: Starting to clear Trash", "CS Trash: looping to PENTAGRAM", "ROF: Calibrated at PENTAGRAM", "ROF: Teleporting directly to PENTAGRAM", "CS: OPEN TP", "CS: Calibrated at PENTAGRAM", "A: Clearing trash betwen Pentagramm & Layoutcheck", "B: Clearing trash betwen Pentagramm & Layoutcheck", "C: Clearing trash betwen Pentagramm & Layoutcheck", "Checking Layout for Vizier", "Checking Layout for De Seis", "Checking Layout for Infector", "Waiting for Diablo to spawn", "End game", "End failed game", "Trying to chicken", "You have died"]
prefix_string = ["A1-L", "A2-Y", "B1-S", "B2-U", "C1-F", "C2-G"]
complex_string = ["Layout_check step 1/2", "Layout_check step 2/2", "Failed to determine the right Layout", "Starting to clear Seal", "Fake: trying to open", "Fake: not", "Fake: is", "Boss: trying to open", "Boss: not", "Boss: is", "Kill Boss", "Static Pathing to Pentagram", "Looping to Pentagram", "finished seal & calibrated at PENTAGRAM"] #"Attacking Vizier at position 1/3", "Attacking De Seis at position", "Attacking Infector at position",
error_string = ["End failed game"]
error_array = []
error_traverse = []
lines_before_error = 10
#refrencevalue START WITH 0
reference_simple = 0
reference_complex = 0
#initialize counter
simple_counter = numpy.zeros (len (simple_string)+1)
complex_counter = numpy.zeros ((len (prefix_string)+1, len (complex_string)+1))

layout_check_counter = 0
#check where layoutcheck 2/2 is
for string in complex_string:
    if "Layout_check step 2/2" in string:
        break
    layout_check_counter += 1



#open file and gather information line by line
log_str = wkdir + "/info.log"
log_file = open (log_str, "r")
log_lines = log_file.readlines ()
traverse_line = 0

line_counter = 0
for line in log_lines:
    if "Traverse: " in line:
        traverse_line = line_counter
    #some temp values for looping
    simple_item_counter = 0
    prefix_counter = 0
    #check simple strings
    for string in simple_string: 
        if string in line:
            simple_counter [simple_item_counter] += 1
            break    
        simple_item_counter += 1
    #check concat strings
    for prefix in prefix_string:
        complex_item_counter = 0
        for string in complex_string:
            if ((prefix + ": " + string) in line):
                complex_counter [prefix_counter][complex_item_counter] += 1
                break
            complex_item_counter += 1
        prefix_counter += 1
    #check error strings
    for error in error_string:
        if error in line:
            error_array.append (log_lines [line_counter-lines_before_error:line_counter])
            error_traverse.append (log_lines [traverse_line])
    line_counter += 1

log_file.close ()
#all lines checked create beatifultable
#some temp values for looping
simple_item_counter = 0
prefix_counter = 0
table1 = BeautifulTable ()
#append simple strings
for string in simple_string:
    table1.rows.append ([string, simple_counter [simple_item_counter], f"{simple_counter [simple_item_counter] / simple_counter [reference_simple]:.0%}"])
    simple_item_counter += 1

result_file = open (wkdir + "/cs_result.txt", 'w')
result_file.write (str(table1))
result_file.write ("\n")

table3 = BeautifulTable ()
table3.rows.append ([complex_counter[0][layout_check_counter], complex_counter[2][layout_check_counter], complex_counter[4][layout_check_counter]])
table3.rows.append (['A2', "B2", "C2"])
table3.rows.append ([complex_counter[1][layout_check_counter], complex_counter[3][layout_check_counter], complex_counter[5][layout_check_counter]])
table3.columns.header = ['A1', 'B1', 'C1']
result_file.write (str(table3))
result_file.write ("\n")



for prefix in prefix_string:
    table2 = BeautifulTable ()
    complex_item_counter = 0
    for string in complex_string:
        table2.rows.append ([prefix + ": " + string, complex_counter [prefix_counter, complex_item_counter], f"{complex_counter [prefix_counter, complex_item_counter]/complex_counter [prefix_counter, reference_complex]:.0%}"])
        complex_item_counter += 1
    prefix_counter += 1
    table2.columns.header = ['String', 'amount', 'percentage']
    result_file.write (str(table2))
    result_file.write ("\n")


error_counter = 0
for error in error_array:
    error_counter += 1
    result_file.write (f"\n ==== LAST " + str(lines_before_error) + " LOG LINES BEFORE FAILED GAME:" + str(error_counter) + error_traverse [error_counter-1] + "\n")
    for line in error:
        result_file.write (line)

Logger.info ("=================================================================================================")
Logger.info ("Parsed info.log - results & details for failed runs stored in cs_result.txt in botty root folder")
Logger.info ("=================================================================================================")
#Logger.info ("\n" + str(table1))