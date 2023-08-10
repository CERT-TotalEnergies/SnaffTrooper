# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

from flask import Flask
from flask import render_template, redirect, url_for
import os
import datetime
import sys
import helper
import prepare_tickets

app = Flask(__name__)

class class_context_manual_processing:
    def __init__(self):
        self.dict_data = None
        self.nb_hit_to_process = None
        self.dict_stats = None
        self.last_file_history = None
        self.csv_status = "UNLOCKED"
        self.current_ticket = 0
        self.filename_for_helper = "manualProcessing"
        self.load_options()

    def load_options(self):
        try:
            self.option_port = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "PORT"))
            self.option_ip = helper.get_clean_options_v2(self.filename_for_helper, specific_option = "IP")
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()
    
    def load_data(self):
        data_history = helper.load_last_results_from_history()
        data_without_already_processed = prepare_tickets.already_processed(data_history[1])
        list_hit_already_notified = data_without_already_processed[1]
        data_without_already_processed = data_without_already_processed[0]
        data_without_excluded_hits = prepare_tickets.exclude_hits(data_without_already_processed)
        self.dict_data_history = data_history[1]
        self.dict_data = data_without_excluded_hits
        self.dict_data = list(sorted(self.dict_data, key=lambda item: item["detection_score"], reverse=True))
        self.nb_hit_to_process = len(self.dict_data)
        self.dict_stats = prepare_tickets.get_stats(data_history)
        self.last_file_history = data_history[0]

@app.route("/")
def index():
    dict_excluded = {}
    list_excluded_hits = helper.read_file("_config", "excluded_hits.txt", write_type = "r")
    
    if(list_excluded_hits != False):
        id_rule = 0
        list_excluded_hits = list_excluded_hits.split("\n")
        for rule in list_excluded_hits:
            dict_excluded["hit_exclusion_rule_"+str(id_rule)] = rule
            id_rule += 1

    list_excluded_sites = helper.read_file("_config", "excluded_sites.txt", write_type = "r")
    if(list_excluded_sites != False):
        list_excluded_sites = list_excluded_sites.split("\n")
        id_rule = 0
        for rule in list_excluded_sites:
            dict_excluded["site_exclusion_rule_"+str(id_rule)] = rule
            id_rule += 1

    if(dict_excluded == {}):
        dict_excluded["No exclusion configured"] = "True"

    dict_excluded["Nb hit to process"] = context_manual_processing.nb_hit_to_process
    message = ""
    return render_template('index.html', dict_stat = context_manual_processing.dict_stats, options = dict_excluded, csv_status = context_manual_processing.csv_status, message = message)

@app.route("/saveCSV")
def saveCSV():
    context_manual_processing.csv_status = "UNLOCKED"
    nb_updated = 0
    for id_hit in range(0, len(context_manual_processing.dict_data_history)):
        for hit_studied in context_manual_processing.dict_data:
            if(hit_studied["url"] == context_manual_processing.dict_data_history[id_hit]["url"]):
                context_manual_processing.dict_data_history[id_hit] = hit_studied
                nb_updated += 1
                break
    if(nb_updated > 0):
        message = f"Hit(s) updated: {nb_updated}"
        helper.print_line(message, context_manual_processing.filename_for_helper, "INFO")

        helper.save_result(context_manual_processing.dict_data_history, context_manual_processing.last_file_history)
        
        message = "CSV saved"
        helper.print_line(message, context_manual_processing.filename_for_helper, "INFO")

    else:
        message = f"No hit to update"
        helper.print_line(message, context_manual_processing.filename_for_helper, "INFO")
        
    return render_template('saveCSV.html', message = message, csv_status = context_manual_processing.csv_status)

@app.route("/ManualEvaluation")
def ManualEvaluation():
    if(context_manual_processing.csv_status == "LOCKED"):
        message = "CSV locked!"
        return render_template('saveCSV.html', message = message, csv_status = context_manual_processing.csv_status)
    else:
        if(context_manual_processing.nb_hit_to_process > 0):
            context_manual_processing.csv_status = "LOCKED"
            message = ""
            filepath = "file:///"+os.getcwd()+"/_downloaded_files_from_sharepoint/"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["id_file"]+"_"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["name"]
            return render_template('manualEvaluation.html', message = message, csv_status = context_manual_processing.csv_status, nb_hit_to_study = context_manual_processing.nb_hit_to_process, info_current_hit = context_manual_processing.dict_data[context_manual_processing.current_ticket], filepath = filepath, current_ticket = context_manual_processing.current_ticket)
        else:
            message = "No ticket to process with current configuration"
            return render_template('saveCSV.html', message = message, csv_status = context_manual_processing.csv_status)

@app.route("/Yes")
def Yes():
    context_manual_processing.dict_data[context_manual_processing.current_ticket]["manual_status"] = "TruePositive"
    context_manual_processing.current_ticket += 1
    if(context_manual_processing.current_ticket < context_manual_processing.nb_hit_to_process):
        message = ""
        filepath = "file:///"+os.getcwd()+"/_downloaded_files_from_sharepoint/"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["id_file"]+"_"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["name"]
        return render_template('manualEvaluation.html', message = message, csv_status = context_manual_processing.csv_status, nb_hit_to_study = context_manual_processing.nb_hit_to_process, info_current_hit = context_manual_processing.dict_data[context_manual_processing.current_ticket], filepath = filepath, current_ticket = context_manual_processing.current_ticket)
    else:
        return redirect(url_for('saveCSV'))

@app.route("/Maybe")
def Maybe():
    context_manual_processing.dict_data[context_manual_processing.current_ticket]["manual_status"] = "MaybeFalsePositive"
    context_manual_processing.current_ticket += 1
    if(context_manual_processing.current_ticket < context_manual_processing.nb_hit_to_process):
        message = ""
        filepath = "file:///"+os.getcwd()+"/_downloaded_files_from_sharepoint/"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["id_file"]+"_"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["name"]
        return render_template('manualEvaluation.html', message = message, csv_status = context_manual_processing.csv_status, nb_hit_to_study = context_manual_processing.nb_hit_to_process, info_current_hit = context_manual_processing.dict_data[context_manual_processing.current_ticket], filepath = filepath, current_ticket = context_manual_processing.current_ticket)
    else:
        return redirect(url_for('saveCSV'))

@app.route("/No")
def No():
    context_manual_processing.dict_data[context_manual_processing.current_ticket]["manual_status"] = "FalsePositive"
    context_manual_processing.current_ticket += 1
    if(context_manual_processing.current_ticket < context_manual_processing.nb_hit_to_process):
        message = ""
        filepath = "file:///"+os.getcwd()+"/_downloaded_files_from_sharepoint/"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["id_file"]+"_"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["name"]
        return render_template('manualEvaluation.html', message = message, csv_status = context_manual_processing.csv_status, nb_hit_to_study = context_manual_processing.nb_hit_to_process, info_current_hit = context_manual_processing.dict_data[context_manual_processing.current_ticket], filepath = filepath, current_ticket = context_manual_processing.current_ticket)
    else:
        return redirect(url_for('saveCSV'))

@app.route("/Previous")
def Previous():
    if(context_manual_processing.current_ticket > 0):
        context_manual_processing.current_ticket -= 1
    if(context_manual_processing.current_ticket < context_manual_processing.nb_hit_to_process):
        message = ""
        filepath = "file:///"+os.getcwd()+"/_downloaded_files_from_sharepoint/"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["id_file"]+"_"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["name"]
        return render_template('manualEvaluation.html', message = message, csv_status = context_manual_processing.csv_status, nb_hit_to_study = context_manual_processing.nb_hit_to_process, info_current_hit = context_manual_processing.dict_data[context_manual_processing.current_ticket], filepath = filepath, current_ticket = context_manual_processing.current_ticket)
    else:
        return redirect(url_for('saveCSV'))

@app.route("/Next")
def Next():
    if(context_manual_processing.current_ticket < context_manual_processing.nb_hit_to_process):
        context_manual_processing.current_ticket += 1
    if(context_manual_processing.current_ticket < context_manual_processing.nb_hit_to_process):
        message = ""
        filepath = "file:///"+os.getcwd()+"/_downloaded_files_from_sharepoint/"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["id_file"]+"_"+context_manual_processing.dict_data[context_manual_processing.current_ticket]["name"]
        return render_template('manualEvaluation.html', message = message, csv_status = context_manual_processing.csv_status, nb_hit_to_study = context_manual_processing.nb_hit_to_process, info_current_hit = context_manual_processing.dict_data[context_manual_processing.current_ticket], filepath = filepath, current_ticket = context_manual_processing.current_ticket)
    else:
        return redirect(url_for('saveCSV'))

def start():
    try:
        context_manual_processing.load_data()
        app.run(host=context_manual_processing.option_ip, port=context_manual_processing.option_port)

    except:
        helper.print_line("No data from manual processing", context_manual_processing.filename_for_helper, "FATAL ERROR")
        exit()

context_manual_processing = class_context_manual_processing()

