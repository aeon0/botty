import os
import numpy
from logger import Logger
from beautifultable import BeautifulTable

wkdir = os.getcwd()

#"Entrance 1 Layout_check step 1/2:", "Entrance 1 Layout_check step 2/2:", "Entrance 1 Layout_check step 1/2:", "Entrance 1 Layout_check step 2/2:", "Entrance 2 Layout_check step 2/2: Failed to determine", "Entrance 2 Layout_check step 2/2: Failed to determine", "CS Entrance Style 1", "CS Entrance Style 2", " - cleaning hall 1/3", " - cleaning hall 2/3", " - cleaning hall 3/3",

#initialize strings
simple_string = [
    "Run Diablo", 
    "ROF: Calibrated at WAYPOINT",
    "ROF: Teleporting directly to PENTAGRAM", 
    
    "ROF: Teleporting to CS ENTRANCE",
    "CS Trash: Calibrated at CS ENTRANCE",
    "CS Trash: Starting to clear Trash",

    "CS Trash: Clearing first hall 1/2",
    "CS Trash: Clearing first hall 2/2",

    "CS Trash (A): Layout_check step 1/2",
    "CS Trash (A): Layout_check step 2/2",
    "CS Trash (A): Layout_check failed",
    
    "CS Trash (A): clearing second hall (1/3)",
    "CS Trash (A): clearing second hall (2/3)",
    "CS Trash (A): clearing second hall (3/3)",

    "CS Trash (A): clearing third hall (1/1)",

    "CS Trash (B): Layout_check step 1/2",
    "CS Trash (B): Layout_check step 2/2",
    "CS Trash (B): Layout_check failed",

    "CS Trash (B): clearing second hall (1/3)",
    "CS Trash (B): clearing second hall (2/3)",
    "CS Trash (B): clearing second hall (3/3)",

    "CS Trash (B): clearing third hall (1/1)",

    "CS Trash: looping to PENTAGRAM", 
    "CS: Calibrated at PENTAGRAM", 
    "CS: OPEN TP",
    "CS: failed to open TP",
    
    "CS TRASH: A Pent to LC",
    "CS TRASH: A looping to PENTAGRAM",
    "CS TRASH: A calibrated at PENTAGRAM",

    "CS TRASH: B Pent to LC",
    "CS TRASH: B looping to PENTAGRAM",
    "CS TRASH: B calibrated at PENTAGRAM",

    "CS TRASH: C Pent to LC",
    "CS TRASH: C looping to PENTAGRAM",
    "CS TRASH: C calibrated at PENTAGRAM",

    "Checking Layout for Vizier", 
    "Checking Layout for De Seis", 
    "Checking Layout for Infector", 
    
    "Waiting for Diablo to spawn", 
    
    "End game", 
    "End failed game", 
    "Trying to chicken", 
    "You have died",

    "Shrine found, activating it",
    "Shrine not found",

    "Got enough pots, no need to go to town right now",
    "Going back to town to visit our friend Jamella",
    "Done in town, now going back to portal",
    "Going through portal",
    "CS after town: Re-open TP",
    "CS after Town: failed to open TP"
    ]
prefix_string = ["A1-L", "A2-Y", "B1-S", "B2-U", "C1-F", "C2-G"]
complex_string = ["Layout_check step 1/2", "Layout_check step 2/2", "Layout_check failure", "Starting to clear Seal",  "Seal1: is closed", "Seal1: is open", "Seal2: is closed", "Seal2: is open", "Kill Boss", "Static Pathing to Pentagram", "Looping to Pentagram", "finished seal & calibrated"]
trash_prefix= [""]
trash_event=[""]
lc_prefix=["Found Match:"]
lc_event=[
        'DIA_NEW_PENT_0', 'DIA_NEW_PENT_1', 'DIA_NEW_PENT_TP', 'DIA_NEW_PENT_2',
        "DIA_A2Y_LAYOUTCHECK0", "DIA_A2Y_LAYOUTCHECK1", "DIA_A2Y_LAYOUTCHECK2", "DIA_A2Y_LAYOUTCHECK4", "DIA_A2Y_LAYOUTCHECK5", "DIA_A2Y_LAYOUTCHECK6", 
        "DIA_A1L_LAYOUTCHECK0", "DIA_A1L_LAYOUTCHECK4", "DIA_A1L_LAYOUTCHECK4LEFT", "DIA_A1L_LAYOUTCHECK1", "DIA_A1L_LAYOUTCHECK2", "DIA_A1L_LAYOUTCHECK3","DIA_A1L_LAYOUTCHECK4RIGHT","DIA_A1L_LAYOUTCHECK5", 
        "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK1", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK2", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK3", 
        "DIA_B2U_LAYOUTCHECK2", "DIA_B2U_LAYOUTCHECK1", "DIA_B2U_LAYOUTCHECK2SMALL","DIA_B2U_LAYOUTCHECK3", "DIA_B2U_LAYOUTCHECK4", "DIA_B2U_LAYOUTCHECK5","DIA_B2U_LAYOUTCHECK6","DIA_B2U_LAYOUTCHECK7","DIA_B2U_LAYOUTCHECK8","DIA_B2U_LAYOUTCHECK9", 
        "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK1", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK4", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK5", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK2", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK3", 
        "DIA_C1F_LAYOUTCHECK1", "DIA_C1F_LAYOUTCHECK2", "DIA_C1F_LAYOUTCHECK3",
        "DIABLO_ENTRANCE_12", "DIABLO_ENTRANCE_13", "DIABLO_ENTRANCE_15", "DIABLO_ENTRANCE_16", "DIABLO_ENTRANCE_19", "DIABLO_ENTRANCE_18","DIABLO_ENTRANCE_50", "DIABLO_ENTRANCE_51", "DIABLO_ENTRANCE_52", "DIABLO_ENTRANCE_53", "DIABLO_ENTRANCE_54", "DIABLO_ENTRANCE_55", 
        "DIABLO_ENTRANCE2_15", "DIABLO_ENTRANCE2_23", "DIABLO_ENTRANCE2_19", "DIABLO_ENTRANCE2_17", "DIABLO_ENTRANCE2_50", "DIABLO_ENTRANCE2_51", "DIABLO_ENTRANCE2_52","DIABLO_ENTRANCE2_53","DIABLO_ENTRANCE2_54","DIABLO_ENTRANCE2_55","DIABLO_ENTRANCE2_56"
        ]
error_string = ["End failed game"]
error_array = []
error_traverse = []
lines_before_error = 30
#refrencevalue START WITH 0
reference_simple = 0
reference_complex = 0
#initialize counter
simple_counter = numpy.zeros (len (simple_string)+1)
complex_counter = numpy.zeros ((len (prefix_string)+1, len (complex_string)+1))
lc_counter = numpy.zeros ((len (lc_prefix)+1, len (lc_event)+1)) 

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
    lc_cl_counter = 0
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
    #check lc_strings
    for pref in lc_prefix:
        lc_item_counter = 0
        for strr in lc_event:
            if ((pref+ " " + strr) in line):
                lc_counter [lc_cl_counter][lc_item_counter] += 1
                break
            lc_item_counter += 1
        lc_cl_counter += 1
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
table1.set_style(BeautifulTable.STYLE_MARKDOWN)
table1.columns.header = ["Event", "#", "%"]
table1.columns.alignment["Event"] = BeautifulTable.ALIGN_LEFT
#append simple strings
for string in simple_string:
    table1.rows.append ([string, f"{round((simple_counter [simple_item_counter]))}", f"{simple_counter [simple_item_counter] / simple_counter [reference_simple]:.0%}"])
    simple_item_counter += 1

result_file = open (wkdir + "/info_log_parsed.txt", 'w')

result_file.write ("======================================================\n")
result_file.write ("                      RUN OVERVIEW                   \n")
result_file.write ("======================================================\n")
result_file.write (str(table1))
result_file.write ("\n")
result_file.write ("\n")

result_file.write ("\n")
result_file.write ("\n")
result_file.write ("===========================================\n")
result_file.write ("                  SEAL RATIO              \n")
result_file.write ("===========================================\n")

table3 = BeautifulTable ()
table3.rows.append ([round(complex_counter[0][layout_check_counter]), round(complex_counter[1][layout_check_counter]), round(complex_counter[2][layout_check_counter]), round(complex_counter[3][layout_check_counter]), round(complex_counter[4][layout_check_counter]), round(complex_counter[5][layout_check_counter]),])
table3.columns.header = ['A1-L', 'A2-Y', 'B1-S', "B2-U",'C1-F', "C2-G"]
table3.set_style(BeautifulTable.STYLE_MARKDOWN)
result_file.write (str(table3))
result_file.write ("\n")
result_file.write ("\n")


result_file.write ("\n")
result_file.write ("\n")
result_file.write ("=================================================\n")
result_file.write ("              INDIVIDUAL SEAL RESULTS           \n")
result_file.write ("=================================================\n")

for prefix in prefix_string:
    table2 = BeautifulTable ()
    complex_item_counter = 0
    for string in complex_string:
        table2.rows.append ([prefix + ": " + string, round(complex_counter [prefix_counter, complex_item_counter]), f"{complex_counter [prefix_counter, complex_item_counter]/complex_counter [prefix_counter, reference_complex]:.0%}"])
        complex_item_counter += 1
    prefix_counter += 1
    table2.columns.header = ['Event', '#', '%']
    table2.set_style(BeautifulTable.STYLE_MARKDOWN)
    table2.columns.header = ["Event", "#", "%"]
    table2.columns.alignment["Event"] = BeautifulTable.ALIGN_LEFT
    result_file.write ("\n")
    result_file.write (str(table2))
    result_file.write ("\n")
result_file.write ("\n")
result_file.write ("\n")

result_file.write ("\n")
result_file.write ("\n")
result_file.write ("=======================================================\n")
result_file.write ("                    TEMPLATES CHECKED                 \n")
result_file.write ("=======================================================\n")


lc_item_counter = 0
lc_cl_counter = 0
table4 = BeautifulTable ()
table4.set_style(BeautifulTable.STYLE_MARKDOWN)
for pre in lc_prefix:
    for item in lc_event:
        table4.rows.append ([pre + " " + item, round(lc_counter[lc_cl_counter][lc_item_counter])])
        lc_item_counter += 1
    lc_cl_counter += 1
table4.columns.header = ["TEMPLATES CHECKED", "#"]
table4.columns.alignment["TEMPLATES CHECKED"] = BeautifulTable.ALIGN_LEFT
result_file.write (str (table4))
result_file.write ("\n")
    
result_file.write ("\n")
result_file.write ("\n")
result_file.write ("========================================================\n")
result_file.write ("           LAST TRAVERSE BEFORE FAILED GAME            \n")
result_file.write ("========================================================\n")
error_counter = 0
for error in error_array:
    error_counter += 1
    result_file.write (error_traverse [error_counter-1])

result_file.write ("\n")
result_file.write ("\n")
result_file.write ("\n")
result_file.write ("==========================================\n")
result_file.write ("   LAST " + str(lines_before_error) + " LOG LINES BEFORE FAILED GAME  \n")
result_file.write ("==========================================\n")
result_file.write ("\n")
error_counter = 0
for error in error_array:
    error_counter += 1
    result_file.write (f"\n" + str(error_counter) + ") ========== " + error_traverse [error_counter-1])
    for line in error:
        result_file.write (line)

Logger.info ("=================================================================================================")
Logger.info ("Parsed info.log - results & details for failed runs stored in " + str(result_file) + " in botty root folder")
Logger.info ("=================================================================================================")
#Logger.info ("\n" + str(table1)) 