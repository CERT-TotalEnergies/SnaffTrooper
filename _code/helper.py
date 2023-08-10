# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

import os
import datetime
import requests
import json
import csv
import xml.etree.ElementTree as ET
import sys

def print_line(to_print, output_file_name, type_print = "INFO"):
    time = datetime.datetime.now()

    time = time.strftime("%Y:%m:%d - %H:%M:%S")
    to_print = f"{time} : [{type_print}] {to_print}"

    print("===========")
    print(to_print)
    print("===========")
    log_filename = sys.argv[0][:-7]+"_logs/"+output_file_name+"_logs.txt"
    try:
        with open(log_filename, "wa") as file_logs:
            file_logs.write(to_print)
            file_logs.write("\n")
    except:
        with open(log_filename, "a") as file_logs:
            file_logs.write(to_print)
            file_logs.write("\n")

def get_public_ip():
    try:
        r = requests.get("https://ipinfo.io/")
        r = r.json()
        public_ip = r["ip"]
    except:
        return("ERROR")
    return(public_ip)

def get_clean_options(scriptname):
    with open(sys.argv[0][:-7]+"_config/options.txt", "r", encoding="UTF-8") as file:
        dict_option = {}
        for line in file:
            if("#" in line):
                pass
            elif(f"{scriptname} - " in line):
                if(line[-1] == "\n"):
                    line = line[:-1]
                option = line.split(" = ")
                option_name = option[0].split(" - ")[1]
                option_conf = option[1]
                dict_option[option_name] = option_conf
    return(dict_option)

def get_clean_options_v2(scriptname, specific_option = None):
    try:
        with open(sys.argv[0][:-7]+"_config/options.txt", "r", encoding="UTF-8") as file:
            dict_option = {}
            for line in file:
                if("#" in line):
                    pass
                elif(f"{scriptname} - " in line):
                    if(line[-1] == "\n"):
                        line = line[:-1]
                    option = line.split(" = ")
                    option_name = option[0].split(" - ")[1]
                    option_conf = option[1]
                    dict_option[option_name] = option_conf
    except:
        print_line("No <_config/options.txt> file!", "helper", type_print = "FATAL ERROR")
        exit()
    if(specific_option != None):
        try:
            return(dict_option[specific_option])
        except:
            message = f"No <{specific_option}> option in <_config/options.txt> file!"
            print_line(message, "helper", type_print = "FATAL ERROR")
            exit()
    else:
        return(dict_option)

def write_file(folder, filename, file_content, write_type = "wb"):
    base_folder = sys.argv[0][:-7]
    file_path = f"{base_folder}{folder}/{filename}"
    try:
        with open(file_path, write_type) as file_to_write:
            file_to_write.write(file_content)
        return(True)
    except Exception as e:
        return(False)

def read_file(folder, filename, write_type = "r"):
    base_folder = sys.argv[0][:-7]
    file_path = f"{base_folder}{folder}/{filename}"
    try:
        with open(file_path, write_type) as file_to_read:
            file_content = file_to_read.read()
        return(file_content)
    except Exception as e:
        return(False)

def get_list_already_downloaded():
    list_downloaded_files = os.listdir(sys.argv[0][:-7]+"_downloaded_files_from_sharepoint")
    list_id_file_downloaded_from_sharepoint = []
    for id_file_downloaded in list_downloaded_files:
        id_file_downloaded = id_file_downloaded.split("_")[0]
        list_id_file_downloaded_from_sharepoint.append(id_file_downloaded)
    return(list_id_file_downloaded_from_sharepoint)


def write_results_csv(consolidated_data, filename, folder, write_type = "w"):
    try:
        fields_names = consolidated_data[0].keys()
        base_folder = sys.argv[0][:-7]
        path_file = f"{base_folder}{folder}/{filename}"
        with open(path_file, "w") as file:
            writer = csv.DictWriter(file, fieldnames = fields_names)
            writer.writeheader()
            writer.writerows(consolidated_data)
        return(True)
    except:
        return(False)

def write_flat_dict(data, filename, folder, write_type = "w"):
    try:
        lines = []
        for key in data:
            lines.append(str(key)+": "+str(data[key]))
        base_folder = sys.argv[0][:-7]
        path_file = f"{base_folder}{folder}/{filename}"
        with open(path_file, "w", encoding = "UTF-8") as file:
            for line in lines:
                file.write(line)
                file.write("\n")
        return(True)
    except:
        return(False)

def manage_stats(dict_stats, counter, nb_to_study, stat_name, save_it = False, rate_stat = 50):
    time = datetime.datetime.now()
    time = time.strftime("%Y:%m:%d - %H:%M:%S")
    write_stat = True

    if(nb_to_study > rate_stat*2):
        if((counter%rate_stat) != 0):
            write_stat = False


    percent = str(int(counter/nb_to_study*100))
    print("************")
    print(f"{time} {stat_name}: {percent}%")
    for key in dict_stats:
        current_stat = dict_stats[key]
        print(f"{key}: {current_stat}")
    print("************")

    if(save_it == True):
        filename = stat_name+".txt"
        if(write_flat_dict(dict_stats, filename, "_logs")):
            return(True)
        else:
            return(False)
    return(True)

def copy_file(src_file, dst_file):
    try:
        with open(src_file, "rb") as fileToCopy:
            content_fileToCopy = fileToCopy.read()

        with open(dst_file, "wb") as fileToWrite:
            fileToWrite.write(content_fileToCopy)
        return(True)
    except:
        return(False)

def import_csv_file(filepath):
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

def create_score_dict_json():
    score_dict = {"score_detection" : { "Black" : 50 , "Red" : 40, "Yellow" : 20, "Green" : 10, "NoRegexCauseBinary" : 10, "RegexNoHit" : 0, "RegexHit" : 20}, "score_source" : {}}

    list_presets = os.listdir(sys.argv[0][:-7]+"_config/_presets_SnaffPoint")
    dict_preset = {}
    for preset in list_presets:
        if(".xml" in preset):       
            tree_preset = ET.parse(sys.argv[0][:-7]+"_config/_presets_SnaffPoint/"+preset)
            root_preset = tree_preset.getroot()
            score_dict["score_source"][root_preset[0].text] = 10
    with open(sys.argv[0][:-7]+"_config/dict_score.json", "w") as file:
        json.dump(score_dict, file, indent = 4)
    return(score_dict)

def load_score_dict_json():
    try:
        with open(sys.argv[0][:-7]+"_config/dict_score.json", "r") as file:
            score_dict = json.loads(file.read())
        print_line("File dict_score.json in <./_config> loaded", "helper", type_print = "INFO")
    except:
        print_line("No file dict_score.json in <./_config>. Default configuration created.", "helper", type_print = "INFO")
        score_dict = create_score_dict_json()
    return(score_dict)

def correct_data_type_from_old_result():
    sharepointUrl = read_file("_config", "targeted_sharepoint.txt", write_type = "r")
    data_scope = "FromSharePoint:"+sharepointUrl
    list_history_files = os.listdir(sys.argv[0][:-7]+"_result_history")
    for file in list_history_files:
        data = import_csv_file(sys.argv[0][:-7]+"_result_history/"+file)
        for id_hit in range(0, len(data)):
            if(data[id_hit]["data_type"] == "FromSharePoint"):
                data[id_hit]["data_type"] = data_scope
        write_results_csv(data, file, sys.argv[0][:-7]+"_result_history")

    list_history_files = os.listdir(sys.argv[0][:-7]+"_results")
    for file in list_history_files:
        data = import_csv_file(sys.argv[0][:-7]+"_results/"+file)
        for id_hit in range(0, len(data)):
            if(data[id_hit]["data_type"] == "FromSharePoint"):
                data[id_hit]["data_type"] = data_scope
        write_results_csv(data, file, sys.argv[0][:-7]+"_results")

def load_last_results_from_history():
    time = datetime.datetime.now()
    time = time.strftime("%Y-%m-%d")

    list_history_files = os.listdir(sys.argv[0][:-7]+"_result_history")
    dict_history_file = {   }
    for history_file in list_history_files:
        time_id_history_file = int(history_file[0:4]+history_file[5:7]+history_file[8:10])*1000000000#bug if more than 9999999 scan in one day
        time_id_history_file += int(history_file[26:-4])
        dict_history_file[time_id_history_file] = history_file
    sorted_dict_history_file = dict(sorted(dict_history_file.items()))
    selected_history_file = list(list(sorted_dict_history_file.items())[-1])[1]

    last_file_history = selected_history_file

    data = import_csv_file(sys.argv[0][:-7]+"_result_history/"+last_file_history)
    return([last_file_history, data])

def save_result(data_processed, last_file_history):
    previous_id = last_file_history.split("_")[-1]
    new_id = int(previous_id[:-4])+1
    filename = last_file_history[:-4-len(str(new_id))]+str(new_id)+".csv"
    folder = "_result_history"

    message = f"Save result in {folder}/{filename}"
    print_line(message, "main", "INFO")

    write_results_csv(data_processed, filename, folder)
    copy_file(sys.argv[0][:-7]+"_result_history/"+filename, sys.argv[0][:-7]+"_results/"+filename[:18]+filename[26:])

class class_context_helper:
    def __init__(self):
        self.filename_for_helper = "helper"

context_helper = class_context_helper()