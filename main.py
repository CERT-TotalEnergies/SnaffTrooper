# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

import os
import sys
import argparse
import pickle

sys.path.append(sys.argv[0][:-7]+"_code")
import helper
import search_on_sharepoint
import get_token
#import study_sharepoint_url_with_graph
import start_snaffler
import add_regex
import archive_results
import clean
import init_context
import parse_snaffler
import study_sharepoint_url
import get_token
import get_token_sharepoint_on_premise
import prepare_tickets
import manual_processing

def start_everything():
    token_f()
    list_f()
    if(context.option_API_to_use == 0):
        helper.print_line("Use SharePoint API", "main", "INFO")
        download_f_SP_version()
    elif(context.option_API_to_use == 1):
        helper.print_line("Use GRAPH API", "main", "INFO")
        download_f_GRAPH_version()
    else:
        helper.print_line("No API selected", "main", "FATAL ERROR")
        exit()
    snaffler_f()
    parse_snaffler_f()
    regex_f()
    archive_f()
    clean_f()

def extraction_f():
    token_f()
    list_f()
    if(context.option_API_to_use == 0):
        helper.print_line("Use SharePoint API", "main", "INFO")
        download_f_SP_version()
    elif(context.option_API_to_use == 1):
        helper.print_line("Use GRAPH API", "main", "INFO")
        download_f_GRAPH_version()
    else:
        helper.print_line("No API selected", "main", "FATAL ERROR")
        exit()

def processing_f():       
    snaffler_f()
    parse_snaffler_f()
    regex_f()
    archive_f()
    clean_f()

def manuel_processing_f():
    manual_processing.start()
    try:
        pass    
    except Exception as e:
        helper.print_line("With manual_processing_f", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()

def prepare_tickets_f():
    try:
        data_history = helper.load_last_results_from_history()
        dict_stats = prepare_tickets.get_stats(data_history)
        data_without_already_processed = prepare_tickets.already_processed(data_history[1])
        list_hit_already_notified = data_without_already_processed[1]
        data_without_already_processed = data_without_already_processed[0]
        data_without_excluded_hits = prepare_tickets.exclude_hits(data_without_already_processed, only_manual = context.option_only_manual_for_ticket)
        top_sites = prepare_tickets.get_top_site(data_without_excluded_hits)
        top_sites = prepare_tickets.exclude_sites(top_sites)
        list_url_excluded_sites = top_sites[1]
        #top_contributors = prepare_tickets.get_top_contributor(data_without_excluded_hits, list_url_excluded_sites)
        top_sites = top_sites[0]
        list_hits_to_notify = prepare_tickets.list_to_notify(data_history[1], top_sites, data_without_excluded_hits)
    except Exception as e:
        helper.print_line("With prepare_tickets", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()

def update_result_from_tickets_f():
    try:
        prepare_tickets.update_result_history_with_external_ticket_id()    
    except Exception as e:
        helper.print_line("With update_result_from_tickets_f", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()

def correct_data_type_from_old_result_f():
    try:
        helper.correct_data_type_from_old_result()
    except Exception as e:
        helper.print_line("With correct_data_type_from_old_result_f", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()

def token_f():
    try:
        sharepoint_targeted = context.sharepoint_targeted+"/"
        if("sharepoint.com" in sharepoint_targeted):
            get_token.ask_required_tokens(context.sharepoint_targeted)
            helper.write_file("_data", "IsOnePrem.txt", "0", write_type = "w")
        else:
            helper.write_file("_data", "IsOnePrem.txt", "1", write_type = "w")
            message = "SharePoint on-premise detected. Use NTLM authentication."
            helper.print_line(message, "main - token_f", "INFO")
        
    except Exception as e:
        helper.print_line("With get_token", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()

def list_f():
    try:
        if (len(os.listdir(sys.argv[0][:-7]+"_config/_presets_SnaffPoint"))>0):
            dict_preset = search_on_sharepoint.load_presets()
            if(helper.read_file("_data", "IsOnePrem.txt", write_type = "r") == "1"):
                dict_preset_with_query = search_on_sharepoint.createSearchQueryNoFQL(dict_preset, 0)
            else:
                dict_preset_with_query = search_on_sharepoint.createSearchQuery(dict_preset, 0)
            sharepoint_targeted = context.sharepoint_targeted 
            
            if(helper.read_file("_data", "IsOnePrem.txt", write_type = "r") == "1"):
                dict_url_recovered = search_on_sharepoint.searchOnSharepointOnPremise(dict_preset_with_query, sharepoint_targeted)
            else:
                dict_url_recovered = search_on_sharepoint.searchOnSharepoint(dict_preset_with_query, sharepoint_targeted)
            
            search_on_sharepoint.write_results_csv(dict_url_recovered)
        else:
            helper.print_line(f"No preset in _presets_SnaffPoint!", "main", "FATAL ERROR")
            exit()    
    except Exception as e:
        helper.print_line("With search_on_sharepoint", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()
    

def download_f_GRAPH_version():
    try:
        helper.print_line("download_f_GRAPH_version - module not present", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()
        """
        list_extracted_data = study_sharepoint_url_with_graph.read_result_search_on_sharepoint(sys.argv[0][:-7]+"_data/results_search_on_sharepoint.csv", context.sharepoint_targeted)
        consolidated_data = []
        for extracted_data in list_extracted_data:
            consolidated_data.extend(study_sharepoint_url_with_graph.study_files(extracted_data, context.sharepoint_targeted))
        study_sharepoint_url_with_graph.write_results_csv(consolidated_data)
        study_sharepoint_url_with_graph.write_stat_read_result()
        """
    except Exception as e:
        helper.print_line("With download_f_GRAPH_version", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()

def download_f_SP_version():
    try:
        study_sharepoint_url.collect(context.sharepoint_targeted)
    except Exception as e:
        helper.print_line("With study_sharepoit_url", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()

def snaffler_f():
    try:
        if(start_snaffler.startSnaffler(context.path_snaffler_binary) == False):
            helper.print_line("Snaffler binary not available", "main", "ERROR")
    except Exception as e:
        helper.print_line("With start_snaffler", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()

def parse_snaffler_f():
    try:
        data_snaffpoint = parse_snaffler.import_snaffpoint_processed(sys.argv[0][:-7]+"_data/results_snaff.csv")
        data_snaffler = parse_snaffler.import_snaffler(sys.argv[0][:-7]+"_data/resultsSnaffler.txt", context.option_API_to_use)
        merged_data = parse_snaffler.merge(data_snaffpoint, data_snaffler)
        parse_snaffler.write_results_csv(merged_data)
    except Exception as e:
        if(context.option_bypass_snaffler_allowed == 1):
            helper.print_line("With parse_snaffler but <ByPassSnafflerAllowed> option set to 1", "main", "ERROR")
            helper.print_line(f"Exception details: {e}", "main", "ERROR")
            helper.print_line(f"Copy SharePoint data as SharePoint data parsed by snaffler", "main", "INFO")
            if(helper.copy_file(sys.argv[0][:-7]+"_data/results_snaff.csv", sys.argv[0][:-7]+"_data/results_snaffpoint_snaffler.csv") == False):
                helper.print_line("With parse_snaffler and <ByPassSnafflerAllowed> option set to 1 - no SharePoint data", "main", "FATAL ERROR")
                exit()
        else:
            helper.print_line("With parse_snaffler and <ByPassSnafflerAllowed> option set to 0", "main", "FATAL ERROR")
            helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
            exit()

def regex_f():
    try:
        data = add_regex.import_merged_result(sys.argv[0][:-7]+"_data/results_snaffpoint_snaffler.csv")
        add_regex.write_results_csv(add_regex.check_if_snaffler(data))
    except Exception as e:
        helper.print_line("With add_regex", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()

def archive_f():
    try:
        dict_data = archive_results.import_merged_result(sys.argv[0][:-7]+"_data/results_snaffpoint_snaffler_regex.csv")
        dict_data_check = archive_results.add_key_if_required(dict_data)
        dict_last_information = archive_results.get_last_information()
        final_data_dict = archive_results.merge_history_and_last(dict_data_check, dict_last_information, context.sharepoint_targeted)
        archive_results.archive_result(final_data_dict)
    except Exception as e:
        helper.print_line("With archive_results", "main", "FATAL ERROR")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()

def clean_f():
    try:
        clean.clean_all()
        clean.pack_logs()
    except Exception as e:
        helper.print_line("FATAL ERROR with clean", "main")
        helper.print_line(f"Exception details: {e}", "main", "FATAL ERROR")
        exit()

def manage_args():
    parser = argparse.ArgumentParser(description="Everything by default!",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-t", "--token", action="store_true", help="get refresh tokens (SharePoint and Graph)")
    parser.add_argument("-l", "--list_sp", action="store_true", help="list from SharePoint (NO DL)")
    parser.add_argument("-d", "--download", action="store_true", help="download the SharePoint results with SharePoint API(no Snaffler)")
    parser.add_argument("-s", "--snaffler", action="store_true", help="Snaffler on the SharePoint results")
    parser.add_argument("-p", "--parse-snaffler", action="store_true", help="Parse snaffler results")
    parser.add_argument("-r", "--regex", action="store_true", help="regex on SharePoint results")
    parser.add_argument("-a", "--archive", action="store_true", help="archive results (and check history)")
    parser.add_argument("-c", "--clean", action="store_true", help="clean at the end (that's not dirty)")
    parser.add_argument("--start", action="store_true", help="start --extraction and --processing")
    parser.add_argument("--extraction", action="store_true", help="only extract data from SharePoint")
    parser.add_argument("--processing", action="store_true", help="process data extracted from SharePoint")
    parser.add_argument("--manual_processing", action="store_true", help="manually check hit before ticket creation")
    parser.add_argument("--tickets", action="store_true", help="prepare tickets at json format")
    parser.add_argument("--update_result_from_tickets", action="store_true", help="update result file with external ticket id from json ticket")
    parser.add_argument("--correct_data_type_from_old_result", action="store_true", help="change data_type of history results with current one")

    args = parser.parse_args()
    config = vars(args)
    return(config)

def main():
    config = manage_args()
    context.init_context()

    helper.print_line("START main.py", "main")
    helper.print_line("Public IP: " + context.public_ip, "main", "INFO")

    at_least_one_arg = False
    if(config["token"] == True):
        at_least_one_arg = True
        token_f()
    if(config["list_sp"] == True):
        at_least_one_arg = True
        list_f()    
    if(config["download"] == True):
        at_least_one_arg = True
        download_f_SP_version()
    if(config["snaffler"] == True):  
        at_least_one_arg = True
        snaffler_f()
    if(config["parse_snaffler"] == True):
        at_least_one_arg = True
        parse_snaffler_f()
    if(config["regex"] == True):
        at_least_one_arg = True
        regex_f()
    if(config["archive"] == True):
        at_least_one_arg = True
        archive_f()
    if(config["clean"] == True):
        at_least_one_arg = True
        clean_f()
    if(config["extraction"] == True):
        at_least_one_arg = True
        extraction_f()
    if(config["processing"] == True):
        at_least_one_arg = True
        processing_f()
    if(config["manual_processing"] == True):
        at_least_one_arg = True
        manuel_processing_f()    
    if(config["tickets"] == True):
        at_least_one_arg = True
        prepare_tickets_f()
    if(config["update_result_from_tickets"] == True):
        at_least_one_arg = True
        update_result_from_tickets_f()
    if(config["correct_data_type_from_old_result"] == True):
        at_least_one_arg = True
        correct_data_type_from_old_result_f()
    if(config["start"] == True):
        at_least_one_arg = True
        start_everything()
    if(at_least_one_arg == False):
        message = "Use --help for help!"
        helper.print_line(message, "main - token_f", "INFO")

    print("====================")
    print("=       EXIT       =")
    print("====================")

class context_variables:
    def init_context(self):
        self.filename_for_helper = "main"
        self.load_options()
        init_context.check_env()
        self.sharepoint_targeted = init_context.check_targeted_sharepoint()
        self.path_snaffler_binary = init_context.check_snaffler_path()
        
        if(self.option_save_public_ip == 1):
            self.public_ip = helper.get_public_ip()
        else:
            self.public_ip = "Configuration sets to not save public IP"
    def load_options(self):
        try:
            self.option_save_public_ip = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "SavePublicIp"))
            self.option_API_to_use = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "UseGraphOrSharePoint"))
            self.option_only_manual_for_ticket = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "OnlyManual"))
            self.option_bypass_snaffler_allowed = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "ByPassSnafflerAllowed"))
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

if __name__ == "__main__":
    print("====================")
    print("=   SnaffTrooper   =")
    print("====================")
    
    context = context_variables()

    if(len(sys.argv) > 1):
        main()
    else:
        print("Use -h for help.")


