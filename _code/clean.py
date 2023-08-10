# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

import os
import datetime
import helper
import sys

def clean_all():
    list_files = os.listdir(sys.argv[0][:-7]+"_data")
    no_save_token = False

    if(context_clean.option_clean_token == 1):
        if("graph_access_token.txt" in list_files):
            message = f"Clean token files"
            helper.print_line(message, context_clean.filename_for_helper, "INFO")
            try:
                os.remove(sys.argv[0][:-7]+"_data/graph_access_token.txt")
            except:
                pass
            try:
                os.remove(sys.argv[0][:-7]+'_data/sharepoint_access_token.txt')
            except:
                pass
            try:
                os.remove(sys.argv[0][:-7]+"_data/graph_refresh_token.txt")
            except:
                pass
            try:
                os.remove(sys.argv[0][:-7]+'_data/sharepoint_refresh_token.txt')
            except:
                pass
            no_save_token = True

    if(context_clean.option_store_data == 1):
        count_data_day = 0
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d_data_")
        list_data_files = []
        if(no_save_token == True):
            list_files = os.listdir(sys.argv[0][:-7]+"_data")
        for file in list_files:
            if("token.txt" in file):
                pass #never packed token
            elif("read_results_url_requested.txt" in file):
                pass #remove this list
            elif(".txt" in file):
                list_data_files.append(file)
            elif(".obj" in file):
                list_data_files.append(file)
            elif(".csv" in file):
                list_data_files.append(file)
            if(time in file):
                count_data_day += 1
        if(len(list_data_files)>0):
            message = f"Store data"
            helper.print_line(message, context_clean.filename_for_helper, "INFO")
            folder_data = time+str(count_data_day)
            os.mkdir(sys.argv[0][:-7]+"_data/"+folder_data)
            for file in list_data_files:
                os.rename(sys.argv[0][:-7]+"_data/"+file, sys.argv[0][:-7]+"_data/"+folder_data+"/"+file)

def pack_logs():
    message = f"Pack logs"
    helper.print_line(message, context_clean.filename_for_helper, "INFO")
    time = datetime.datetime.now()
    time = time.strftime("%Y-%m-%d_logs_")
    count_log_day = 0

    list_files = os.listdir(sys.argv[0][:-7]+"_logs")
    list_log_files = []
    for file in list_files:
        if(".txt" in file):
            list_log_files.append(file)
        if(time in file):
            count_log_day += 1

    folder_logs = time+str(count_log_day)
    os.mkdir(sys.argv[0][:-7]+"_logs/"+folder_logs)

    for file in list_log_files:
        try:
            if("clean_logs" in file):
                pass
            else:
                os.rename(sys.argv[0][:-7]+"_logs/"+file, sys.argv[0][:-7]+"_logs/"+folder_logs+"/"+file)
        except:
            message = f"no log file {file}"
            helper.print_line(message, context_clean.filename_for_helper, "ERROR")
    os.rename(sys.argv[0][:-7]+"_logs/clean_logs.txt", sys.argv[0][:-7]+"_logs/"+folder_logs+"/"+"clean_logs.txt")

class class_context_clean:
    def __init__(self):
        self.filename_for_helper = "clean"
        self.load_options()

    def load_options(self):
        try:
            self.option_clean_token = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "CLEAN_TOKEN"))
            self.option_store_data = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "STORE_DATA"))
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

context_clean = class_context_clean()


