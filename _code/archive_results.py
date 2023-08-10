# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

"""
Be carefull with hundreds of archived results files.
You maybe want to modify configuration file to: "archive - REVIEW_ALL = 0"

"""

import csv
import datetime
import os
import helper
import sys

def import_merged_result(filepath):
    data = []
    with open(filepath, newline='\n') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    list_key = data[0]
    dict_data = []
    for d in data[1:]:
        data_to_append = {}
        count = 0
        for key in list_key:
            data_to_append[key] = d[count]
            count +=1

        dict_data.append(data_to_append)
    return(dict_data)

def add_key_if_required(dict_data):
    mandatory_keys = ['source_type', 'id_file', 'file_status', 'data_type', 'url', 'createdDateTime', 'lastModifiedDateTime', 'size', 'name', 'mimeType', 'createdBy', 'createdBy_dpt', 'downloadUrl', 'detection_type', 'detection_rule', 'context', 'first_scan_detection_date']
    additional_keys = ['last_scan_detection_date','detection_score', 'manual_status', 'still_present', 'already_notified']    

    dict_data_check = []

    for data in dict_data:
        temp_dict = {}
        for key in mandatory_keys:
            try:
                temp_dict[key] = data[key]
            except:
                temp_dict[key] = ""

        for key in additional_keys:
            temp_dict[key] = ""

        dict_data_check.append(temp_dict)
    return(dict_data_check)

def archive_result(dict_data_check):
    time = datetime.datetime.now()
    time = time.strftime("%Y-%m-%d")

    list_history_files = os.listdir(sys.argv[0][:-7]+"_result_history")
    count_result_of_day = 0
    for alread_saved in list_history_files:
        if(time in alread_saved):
            count_result_of_day += 1

    filename = time+"_result_history_"+str(count_result_of_day)+".csv"

    fields_names = dict_data_check[0].keys()
    max_fields = 0
    for i in dict_data_check:#need to verify if this is still usefull
        if(len(i)>max_fields):
            max_fields = len(i)
            fields_names = i.keys()
    path_to_save = sys.argv[0][:-7]+'_result_history/'+filename

    with open(path_to_save, "w") as file:
        writer = csv.DictWriter(file, fieldnames = fields_names)
        writer.writeheader()
        writer.writerows(dict_data_check)


    filename = time+"_result_"+str(count_result_of_day)+".csv" #save twice
    path_to_save = sys.argv[0][:-7]+'_results/'+filename
    
    with open(path_to_save, "w") as file:
        writer = csv.DictWriter(file, fieldnames = fields_names)
        writer.writeheader()
        writer.writerows(dict_data_check)

    message = f"Archive: {filename}"
    helper.print_line(message, context_archive_results.filename_for_helper, "INFO")

def comp_date_stored(date1, date2, maxOrMin):
    
    try:
        date1_int = int(date1[0:4]+date1[5:7]+date1[8:10])
    except:
        date1_int = 0
    try:
        date2_int = int(date2[0:4]+date2[5:7]+date2[8:10])
    except:
        date2_int = 0

    if(date1_int + date2_int == 0):
        return("")

    if(date1_int > date2_int):
        max_date = date1
        min_date = date2
    else:
        max_date = date2
        min_date = date1

    if(maxOrMin == "max"):
        return(max_date)
    elif(maxOrMin == "min"):
        return(min_date)
    else:
        message = "ERROR: incorrect arg on comp_date_stored"
        helper.print_line(message, context_archive_results.filename_for_helper, "ERROR")

def read_all_history(sorted_dict_history_file):
    dict_last_information = []
    list_file_to_read = []

    temp_dict = {}
    for filename in sorted_dict_history_file.items():
        list_file_to_read.append(list(filename)[1])

    for filename in list_file_to_read:
        dict_data = import_merged_result(sys.argv[0][:-7]+"_result_history/"+filename)
        for data in dict_data:
            curr_id = data["url"]+data["id_file"]
            make_comp = False
            try:
                previous_temp_dict_data = temp_dict[curr_id]
                make_comp = True

            except Exception as e:
                temp_dict[curr_id] = data

            if(make_comp == True):
                temp_dict[curr_id]["first_scan_detection_date"] = comp_date_stored(temp_dict[curr_id]["first_scan_detection_date"], data["first_scan_detection_date"], "min")
                temp_dict[curr_id]["last_scan_detection_date"] = comp_date_stored(temp_dict[curr_id]["last_scan_detection_date"], data["last_scan_detection_date"], "max")

                if(data["manual_status"] != ""):
                    temp_dict[curr_id]["manual_status"] = data["manual_status"]#take the more recent one
                if(data["already_notified"] != ""):
                    temp_dict[curr_id]["already_notified"] = data["already_notified"]#take the more recent one
    
    for data in temp_dict:
        dict_last_information.append(temp_dict[data])
    return(dict_last_information)

def get_last_information():
    dict_last_information = []

    review_all = context_archive_results.option_review_all
    verbose_log = context_archive_results.option_verbose_log

    list_history_files = os.listdir(sys.argv[0][:-7]+"_result_history")
    dict_history_file = {}
    if(len(list_history_files)>0):
        for history_file in list_history_files:
            time_id_history_file = int(history_file[0:4]+history_file[5:7]+history_file[8:10])*1000000000#bug if more than 9999999 scans in one day
            time_id_history_file += int(history_file[26:-4])

            dict_history_file[time_id_history_file] = history_file

        sorted_dict_history_file = dict(sorted(dict_history_file.items()))
        
        if(int(review_all) == 0):
            selected_history_file = list(list(sorted_dict_history_file.items())[-1])[1]
            dict_last_information = import_merged_result(sys.argv[0][:-7]+"_result_history/"+selected_history_file)
            message ="Load history from: "+selected_history_file
            helper.print_line(message, context_archive_results.filename_for_helper, "INFO")
        else:
            message = "Review all history"
            helper.print_line(message, context_archive_results.filename_for_helper, "INFO")
            dict_last_information = read_all_history(sorted_dict_history_file)
            #print information?
    return(dict_last_information)

def merge_history_and_last(dict_data_check, dict_last_information, sharepointUrl):
    score_dict = helper.load_score_dict_json()
    real_dict_data = {}
    real_dict_hist = {}
    final_data_dict = []
    count_history = 0
    count_no_history = 0
    count_no_more_present = 0
    count_history_not_in_scope = 0

    review_all = context_archive_results.option_review_all
    verbose_log = context_archive_results.option_verbose_log

    for data in dict_data_check:
        real_dict_data[str(data["id_file"])+"_"+str(data["url"])] = data
    for data in dict_last_information:
        real_dict_hist[str(data["id_file"])+"_"+str(data["url"])] = data

    for data in real_dict_data:
        try:
            history_data = real_dict_hist[data]
            data = real_dict_data[data]
            #use history data to save manual status and ticket
            data["manual_status"] = history_data["manual_status"]
            data["still_present"] = "1"
            data["detection_score"] = detection_score_calculation(data["detection_type"], data["source_type"], score_dict)
            data["already_notified"] = history_data["already_notified"]
            data["last_scan_detection_date"] = data["first_scan_detection_date"]
            data["first_scan_detection_date"] = history_data["first_scan_detection_date"]

            final_data_dict.append(data)
            url = data["url"]
            if(verbose_log == 1):
                message = f"History for: {url}"
                helper.print_line(message, context_archive_results.filename_for_helper, "INFO")
            count_history += 1
        except Exception as e:
            data = real_dict_data[data]
            data["still_present"] = "1"
            data["detection_score"] = detection_score_calculation(data["detection_type"], data["source_type"], score_dict)
            final_data_dict.append(data)
            url = data["url"]
            if(verbose_log == 1):
                message = f"No history for: {url}"
                helper.print_line(message, context_archive_results.filename_for_helper, "INFO")
            count_no_history += 1
    #add history
    data_scope = "FromSharePoint:"+sharepointUrl
    for data in real_dict_hist:
        try:
            already_in = real_dict_data[data]
        except:
            data = real_dict_hist[data]
            if(data["data_type"] == data_scope):
                data["still_present"] = "0"
                count_no_more_present += 1
            else:
                count_history_not_in_scope += 1
            data["detection_score"] = detection_score_calculation(data["detection_type"], data["source_type"], score_dict)
            final_data_dict.append(data)

    message = f"History for: {count_history} record(s)"
    helper.print_line(message, context_archive_results.filename_for_helper, "INFO")
    message = f"No history for: {count_no_history} record(s)"
    helper.print_line(message, context_archive_results.filename_for_helper, "INFO")
    message = f"No more present for: {count_no_more_present} record(s)"
    helper.print_line(message, context_archive_results.filename_for_helper, "INFO")
    message = f"Hit history but not in scope: {count_history_not_in_scope} record(s)"
    helper.print_line(message, context_archive_results.filename_for_helper, "INFO")
    return(final_data_dict)

def detection_score_calculation(detection_type, source_type, score_dict):
    score = 0
    for hint_score in score_dict["score_detection"]:
        if(hint_score in detection_type):
            score += score_dict["score_detection"][hint_score]
    is_match = False
    for hint_score in score_dict["score_source"]:
        if(hint_score == source_type):
            score += score_dict["score_source"][hint_score]
            is_match = True
            break
    if(is_match == False):
        message = f"No score for: {source_type}"
        helper.print_line(message, context_archive_results.filename_for_helper, "ERROR")
    return(score)

class class_context_archive_results:
    def __init__(self):
        self.filename_for_helper = "archiveResults"
        self.load_options()

    def load_options(self):
        try:
            self.option_review_all = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "REVIEW_ALL"))
            self.option_verbose_log = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "VERBOSE_LOG"))
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

context_archive_results = class_context_archive_results()




