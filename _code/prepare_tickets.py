# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

import helper
import helper_sharepoint
from pprint import pprint as ppt
import csv
import os
import datetime
import sys
import json
import hashlib

def get_stats(data_history):
    data = data_history
    last_file_history = data[0]
    data = data[1]
    nb_data = len(data)

    dict_stats = {}
    dict_stats["file_loaded"] = last_file_history

    dict_stats["Hit"] = nb_data

    nb_new_since_last_scan = 0
    nb_still_present = 0
    nb_with_ticket = 0
    nb_manual_status = 0
    dict_manual_status = {}

    for info in data:
        if(info["already_notified"] != ""):
            nb_with_ticket += 1
        if(info["still_present"] == "1"):
            nb_still_present += 1
        if(info["last_scan_detection_date"] == "" and info["still_present"] == "1"):
            nb_new_since_last_scan += 1
        if(info["manual_status"] != ""):
            nb_manual_status += 1
            try:
                dict_manual_status[info["manual_status"]] += 1
            except:
                dict_manual_status[info["manual_status"]] = 1

    dict_stats["nb_new_since_last_scan"] = nb_new_since_last_scan
    dict_stats["nb_still_present"] = nb_still_present
    dict_stats["nb_with_ticket"] = nb_with_ticket
    dict_stats["manual_status"] = nb_manual_status
    dict_stats["detail_manual_status"] = dict_manual_status

    message = f"File loaded : {last_file_history}"
    helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
    for key in dict_stats:
        if(type(dict_stats[key]) == type(1)):
            message = f"Stat - {key} - {dict_stats[key]}"
            helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
    for key in dict_stats["detail_manual_status"]:
        nb = dict_stats["detail_manual_status"][key]
        message = f"Stat - Manual status : {key} - {nb}"
        helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")

    return(dict_stats)

def already_processed(data):
    data_without_already_processed = []
    list_hit_already_notified = []
    nb_alread_processed = 0
    for hit in data:
        if(hit["already_notified"] == "" and hit["manual_status"] == ""):
            data_without_already_processed.append(hit)
        elif(hit["manual_status"] == "TruePositive"):
            data_without_already_processed.append(hit)
        elif(hit["already_notified"] != ""):
            list_hit_already_notified.append(hit)
            nb_alread_processed += 1
        else:
            nb_alread_processed += 1

    message = f"Remove {nb_alread_processed} already processed hits"
    helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
    return([data_without_already_processed, list_hit_already_notified])

def exclude_hits(data, only_manual = False):
    verbosity = context_prepare_tickets.option_verbosity
    data_without_excluded_hits = []
    list_excluded_hits = helper.read_file("_config", "excluded_hits.txt", write_type = "r")
    rule_exclude_hits = []
    if(list_excluded_hits == False):
        message = f"No excluded hits configured in /_config/excluded_hits.txt"
        helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
    else:
        list_excluded_hits = list_excluded_hits.split("\n")
        for rule in list_excluded_hits:
            try:
                splitted_rule = rule.split(" = ")
                if(splitted_rule[1] == "*!NOCONTENT!*"):
                    rule_exclude_hits.append([splitted_rule[0], "","CLASSIC"])
                elif(splitted_rule[1] == "*!1!*"):
                    rule_exclude_hits.append([splitted_rule[0], "","TRUE"])
                elif(splitted_rule[1] == "*!0!*"):
                    rule_exclude_hits.append([splitted_rule[0], "","FALSE"])
                elif(splitted_rule[1][0] == "*" and splitted_rule[1][-1] == "*"):
                    rule_exclude_hits.append([splitted_rule[0], splitted_rule[1][1:-1],"IN"])
                elif(splitted_rule[1][0] == "*"):
                    rule_exclude_hits.append([splitted_rule[0], splitted_rule[1][1:],"END", len(splitted_rule[1])-1])
                elif(splitted_rule[1][-1] == "*"):
                    rule_exclude_hits.append([splitted_rule[0], splitted_rule[1][:-1],"START", len(splitted_rule[1])-1])
                else:
                    rule_exclude_hits.append([splitted_rule[0], splitted_rule[1],"CLASSIC"])
            except:
                message = f"Bad rule in /_config/excluded_hits.txt - {rule}"
                helper.print_line(message, context_prepare_tickets.filename_for_helper, "ERROR")

    nb_excluded = 0

    for hit in data:
        is_excluded = False
        id_file = hit["id_file"]
        name_file = hit["name"]

        if(only_manual == 1):
            if(hit["manual_status"] != "TruePositive"):
                is_excluded = True

        if(is_excluded == False):
            for rule in rule_exclude_hits:
                try:
                    if(rule[2] == "CLASSIC"):
                        if(hit[rule[0]] == rule[1]):
                            is_excluded = True
                            break
                    elif(rule[2] == "IN"):
                        if(rule[1] in hit[rule[0]]):
                            is_excluded = True
                            break
                    elif(rule[2] == "TRUE"):
                        if(hit[rule[0]] == 1):
                            is_excluded = True
                            break
                    elif(rule[2] == "FALSE"):
                        if(hit[rule[0]] == 0):
                            is_excluded = True
                            break
                    elif(rule[2] == "END"):
                        if(rule[1] in hit[rule[0]]):
                            if(hit[rule[0]][-int(rule[3]):] == rule[1]):
                                is_excluded = True
                                break
                    elif(rule[2] == "START"):
                        if(rule[1] in hit[rule[0]]):
                            if(hit[rule[0]][:int(rule[3])] == rule[1]):
                                is_excluded = True
                                break
                except:
                    message = f"Processing excluded hits with: {rule} for {id_file}"
                    helper.print_line(message, context_prepare_tickets.filename_for_helper, "ERROR")
        if(is_excluded == True):
            if(verbosity == 1):
                message = f"Exclude: {id_file} ({name_file} - RULE: {rule})"
                helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
            nb_excluded += 1
        else:
            data_without_excluded_hits.append(hit)

    message = f"Number of excluded hits: {nb_excluded}"
    helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
    return(data_without_excluded_hits)

def get_top_contributor(data, list_url_excluded_sites):
    dict_contributor = {}
    nb_excluded = 0
    for hit in data:
        is_excluded_by_site = False
        for excluded_site in list_url_excluded_sites:
            if excluded_site in hit["url"]:
                is_excluded_by_site = True
                break

        if(is_excluded_by_site == False):
            contributor = hit["createdBy"]
            if(contributor == ""):
                contributor = "unknown"
            try:
                dict_contributor[contributor] += 1
            except:
                dict_contributor[contributor] = 1
        else:
            nb_excluded += 1

    message = f"Number of excluded hits caused by site exclusion: {nb_excluded}"
    return((sorted(dict_contributor.items(), key=lambda item: item[1])))

def get_top_site(data):
    #note: on premise there is no "site" keyword
    dict_site = {}
    for hit in data:
        url = hit["url"]
        url_splitted = url.split("/")
        if("site" in url):
            id_part = 0
            site_url = ""
            while(id_part < len(url_splitted)):
                id_part += 1
                if(url_splitted[id_part] == "sites"):
                    for id_part_rebuild in range(0, id_part+2):
                        site_url = site_url+"/"+url_splitted[id_part_rebuild]
                    site_url = site_url[1:]
                    break
        else:
            site_url = ""
            for id_part_rebuild in range(0, 4):
                site_url = site_url+"/"+url_splitted[id_part_rebuild]
            site_url = site_url[1:]
        try:
            dict_site[site_url] += 1
        except:
            dict_site[site_url] = 1
    return(dict_site)

def exclude_sites(top_sites):
    list_excluded_sites = helper.read_file("_config", "excluded_sites.txt", write_type = "r")
    list_url_excluded_sites = []
    if(list_excluded_sites == False):
        message = f"No excluded site configured in /_config/excluded_sites.txt"
        helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
        return([top_sites, list_url_excluded_sites])
    else:
        list_excluded_sites = list_excluded_sites.split("\n")
        top_sites_with_excluded_sites = {}
        nb_sites_excluded = len(list_excluded_sites)
        message = f"{nb_sites_excluded} sites excluded"
        helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
        for site in top_sites:
            contains_excluded = False
            for excluded_site in list_excluded_sites:
                if(excluded_site in site):
                    contains_excluded = True
            if(contains_excluded == False):
                top_sites_with_excluded_sites[site] = top_sites[site]
            else:
                associated_hits = top_sites[site]
                message = f"Site: {site} with {associated_hits} hits excluded"
                helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
                list_url_excluded_sites.append(site)
    return([top_sites_with_excluded_sites, list_url_excluded_sites])

def get_number_user_by_site(data):
    list_concerned_sites = get_top_site(data)
    dict_user_by_site = {}
    for site in list_concerned_sites:
        for hit in data:
            if(site in hit["url"]):
                if(hit["createdBy"] == ""):
                    try:
                        dict_user_by_site[site]["unknown"][0] += 1
                        if hit["already_notified"] not in dict_user_by_site[site][hit["createdBy"]][1]:
                            dict_user_by_site[site][hit["createdBy"]][1].append(hit["already_notified"])
                    except:
                        try:
                            dict_user_by_site[site]["unknown"] = [1,[hit["already_notified"]]]
                        except:
                            dict_user_by_site[site] = {"unknown":[1,[hit["already_notified"]]]}
                else:
                    try:
                        dict_user_by_site[site][hit["createdBy"]][0] += 1
                        if hit["already_notified"] not in dict_user_by_site[site][hit["createdBy"]][1]:
                            dict_user_by_site[site][hit["createdBy"]][1].append(hit["already_notified"])
                    except:
                        try:
                            dict_user_by_site[site][hit["createdBy"]] = [1,[hit["already_notified"]]]
                        except:
                            dict_user_by_site[site] = {hit["createdBy"]:[1,[hit["already_notified"]]]}
    return(dict_user_by_site)

def get_number_site_by_user(data):#todo check
    list_concerned_sites = get_top_site(data)
    dict_site_by_user = {}
    
    for hit in data:
        if(hit["createdBy"] == ""):
            creator = "unknown"
        else:
            creator = hit["createdBy"]
        for site in list_concerned_sites:
            if(site in hit["url"]):
                try:
                    dict_site_by_user[creator][site][0] += 1
                    if hit["already_notified"] not in dict_site_by_user[creator][site][1]:
                        dict_site_by_user[creator][site][1].append(hit["already_notified"])
                except:
                    try:
                        dict_site_by_user[creator][site] = [1, [hit["already_notified"]]]
                    except:
                        dict_site_by_user[creator] = {site : [1, [hit["already_notified"]]]}
    return(dict_site_by_user)

def load_json_tickets():
    dict_tickets = {}
    list_name_json_tickets = os.listdir(sys.argv[0][:-7]+"_tickets")
    nb_ticket_loaded = 0
    nb_ticket_loading_error = 0
    for ticket_name in list_name_json_tickets:
        if(len(ticket_name) > 5):
            if(ticket_name[-5:] == ".json"):
                try:
                    with open(sys.argv[0][:-7]+"_tickets/"+ticket_name, "r") as ticket_file:
                        dict_tickets[ticket_name[:-5]] = json.loads(ticket_file.read())
                    nb_ticket_loaded += 1
                except:
                    message = "with loading {ticket_name}"
                    helper.print_line(message, context_prepare_tickets.filename_for_helper, "ERROR")
                    nb_ticket_loading_error += 1

    message = f"{nb_ticket_loaded} tickets loaded and {nb_ticket_loading_error} loading ticket error(s)"
    helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
    return(dict_tickets)

def recreate_json_tickets(dict_tickets, all_hits):
    #if no json for ticket id in .CSV
    time = datetime.datetime.now()
    time = time.strftime("%Y-%m-%d")

    dict_ticket_to_create = {}

    dict_external_tickets = {}
    nb_hits_with_external_ticket_id_in_csv = 0

    for hit in all_hits:
        if(hit["already_notified"] != ""):
            try:
                dict_external_tickets[hit["already_notified"]].append(hit)
            except:
                dict_external_tickets[hit["already_notified"]] = [hit]
            nb_hits_with_external_ticket_id_in_csv += 1
    
    message = f"{nb_hits_with_external_ticket_id_in_csv} hits with external ticket id"
    helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")

    list_external_ticket_id_to_create_json = []
    for external_ticket_id in dict_external_tickets:
        is_json_ticket = False
        for ticket in dict_tickets:
            if(dict_tickets[ticket]["id_ticket_ext"] == external_ticket_id):
                is_json_ticket = True
        if(is_json_ticket == False):
            list_external_ticket_id_to_create_json.append(external_ticket_id)

    nb_ticket_to_create = len(list_external_ticket_id_to_create_json)
    message = f"{nb_ticket_to_create} tickets will be created since not in folder <./_tickets>"
    helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")

    for id_ticket_ext in list_external_ticket_id_to_create_json:
        dict_data_type = {}
        for hit in dict_external_tickets[id_ticket_ext]:
            try:
                dict_data_type[hit["data_type"]].append(hit)
            except:
                dict_data_type[hit["data_type"]] = [hit]

        for info_ticket_perimeter in dict_data_type:
            info_ticket_type = "MISC" #MISC ticket cause information unknown
            info_ticket_status = "POSTED"
            info_ticket_id_ticket_ext = id_ticket_ext

            info_site_by_user = get_number_site_by_user(dict_data_type[info_ticket_perimeter])
            info_user_by_site = get_number_user_by_site(dict_data_type[info_ticket_perimeter])

            average_detection_score = 0
            for hit_for_score in dict_external_tickets[id_ticket_ext]:
                average_detection_score += int(hit_for_score["detection_score"])
            nb_hits_ticket = len(dict_external_tickets[id_ticket_ext])
            average_detection_score = int(average_detection_score / nb_hits_ticket)

            info_ticket_hit_resume = {"average_detection_score" : average_detection_score, "nb_hits" : nb_hits_ticket, "nb_concerned_users" : len(info_site_by_user), "nb_concerned_sites" : len(info_user_by_site)}
            info_ticket_hit_infos = {"concerned_users" : list(info_site_by_user.keys()), "concerned_sites" : list(info_user_by_site.keys())}
            info_ticket_hit = dict_external_tickets[id_ticket_ext]
            info_ticket_linked = ""

            info_ticket_rev = 0

            data_ticket = {"type" : info_ticket_type, "rev":info_ticket_rev, "linked_ticket" : info_ticket_linked, "perimeter" : info_ticket_perimeter, "status" : info_ticket_status, "id_ticket_ext" : info_ticket_id_ticket_ext, "hit_resume" : info_ticket_hit_resume, "hit_infos" : info_ticket_hit_infos, "hit" : info_ticket_hit}
            
            id_ticket = time+"_"+info_ticket_type+"_"+hashlib.sha256(json.dumps(data_ticket, indent = 4).encode('utf-8')).hexdigest()
            dict_ticket_to_create[id_ticket] = data_ticket
            dict_tickets[id_ticket] = data_ticket

    create_ticket(dict_ticket_to_create)

    return(dict_tickets)

def create_ticket(dict_tickets):
    for id_ticket in dict_tickets:
        ticket_name = sys.argv[0][:-7]+"_tickets/"+id_ticket+".json"
        with open(ticket_name, "w") as ticket_file:
            json.dump(dict_tickets[id_ticket], ticket_file, indent = 4)
        message = f"{id_ticket} was saved to <./_tickets>"
        helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")

def update_ticket_site(dict_tickets, list_hit_with_ticket, dict_existing_ticket_by_site):
    for site in dict_existing_ticket_by_site:
        is_updated = False
        for ticket_name in dict_existing_ticket_by_site[site]:#will update first NEW ticket
            if(dict_tickets[ticket_name]["status"] == "NEW"):
                hit_to_add = []
                for hit in list_hit_with_ticket:
                    if(site in hit["url"]):
                        hit_to_add.append(hit)

                nb_hit_to_add = len(hit_to_add)
                if(nb_hit_to_add > 0):
                    dict_tickets[ticket_name]["rev"] = dict_tickets[ticket_name]["rev"]+1
                    dict_tickets[ticket_name]["hit"].extend(hit_to_add)

                    info_site_by_user = get_number_site_by_user(hit_to_add)
                    info_user_by_site = get_number_user_by_site(hit_to_add)

                    average_detection_score = 0
                    for hit_for_score in dict_tickets[ticket_name]["hit"]:
                        average_detection_score += int(hit_for_score["detection_score"])
                    nb_hits_ticket = len(dict_tickets[ticket_name]["hit"])
                    average_detection_score = int(average_detection_score / nb_hits_ticket)

                    info_ticket_hit_resume = {"average_detection_score" : average_detection_score, "nb_hits" : nb_hits_ticket , "nb_concerned_users" : len(info_site_by_user), "nb_concerned_sites" : len(info_user_by_site)}
                    info_ticket_hit_infos = {"concerned_users" : list(info_site_by_user.keys()), "concerned_sites" : list(info_user_by_site.keys())}

                    dict_tickets[ticket_name]["hit_resume"] = info_ticket_hit_resume
                    dict_tickets[ticket_name]["hit_infos"] = info_ticket_hit_infos

                    message = f"Update {ticket_name} with {nb_hit_to_add} hits!"
                    helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
                    is_updated = True

                else:
                    message = f"No hit to add to {ticket_name}"
                    helper.print_line(message, context_prepare_tickets.filename_for_helper, "ERROR")
        if(is_updated == False):
            message = f"Create new ticket because ERROR or existing ticket status is POSTED"
            helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")

            info_ticket_type = "MISC" #MISC ticket cause ERROR of already posted existing ticket
            info_ticket_status = "NEW"
            info_ticket_id_ticket_ext = ""

            info_site_by_user = get_number_site_by_user(hit_to_add)
            info_user_by_site = get_number_user_by_site(hit_to_add)

            average_detection_score = 0
            for hit_for_score in hit_to_add:
                average_detection_score += int(hit_for_score["detection_score"])
            nb_hits_ticket = len(hit_to_add)
            average_detection_score = int(average_detection_score / nb_hits_ticket)


            info_ticket_hit_resume = {"average_detection_score" : average_detection_score,"nb_hits" : len(hit_to_add), "nb_concerned_users" : len(info_site_by_user), "nb_concerned_sites" : len(info_user_by_site)}
            info_ticket_hit_infos = {"concerned_users" : list(info_site_by_user.keys()), "concerned_sites" : list(info_user_by_site.keys())}

            info_ticket_hit = hit_to_add
            info_ticket_linked = dict_existing_ticket_by_site[site]

            info_ticket_rev = 0

            data_ticket = {"type" : info_ticket_type, "rev":info_ticket_rev, "linked_ticket" : info_ticket_linked, "perimeter" : info_ticket_perimeter, "status" : info_ticket_status, "id_ticket_ext" : info_ticket_id_ticket_ext, "hit_resume" : info_ticket_hit_resume, "hit_infos" : info_ticket_hit_infos, "hit" : info_ticket_hit}
            
            id_ticket = time+"_"+info_ticket_type+"_"+hashlib.sha256(json.dumps(data_ticket, indent = 4).encode('utf-8')).hexdigest()
            dict_tickets[id_ticket] = data_ticket

    return(dict_tickets)

def list_to_notify(all_hits, top_sites, data_without_excluded_hits):
    limit_hit_to_notify_site = context_prepare_tickets.option_limit_hit_to_notify_site

    dict_tickets = load_json_tickets()

    dict_tickets = recreate_json_tickets(dict_tickets, all_hits)

    list_url_with_json_ticket = []
    for ticket in dict_tickets:
        for hit in dict_tickets[ticket]["hit"]:
            list_url_with_json_ticket.append(hit["url"])

    nb_hit_already_in_json_ticket = 0
    data_without_excluded_hits_and_json_ticket = []
    for hit in data_without_excluded_hits:
        if(hit["url"] in list_url_with_json_ticket):
            nb_hit_already_in_json_ticket += 1
        else:
            data_without_excluded_hits_and_json_ticket.append(hit)

    message = f"Exclude {nb_hit_already_in_json_ticket} hits since already json ticket and no external_ticket_id"
    helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")

    dict_existing_ticket_by_site = {}
    for ticket_name in dict_tickets:
        if(dict_tickets[ticket_name]["type"] == "SITE"):
            for site in dict_tickets[ticket_name]["hit_infos"]["concerned_sites"]:
                try:
                    dict_existing_ticket_by_site[site].append(ticket_name)
                except:
                    dict_existing_ticket_by_site[site] = [ticket_name]
    
    list_hit_with_ticket = []
    list_hit_without_ticket = []
    for hit in data_without_excluded_hits_and_json_ticket:
        with_ticket = False
        for site_from_existing_ticket in dict_existing_ticket_by_site:
            if(site_from_existing_ticket in hit["url"]):
                with_ticket = True
                list_hit_with_ticket.append(hit)
                break
        if(with_ticket == False):
            list_hit_without_ticket.append(hit)

    if(len(list_hit_with_ticket) > 0):
        dict_tickets = update_ticket_site(dict_tickets, list_hit_with_ticket, dict_existing_ticket_by_site)

    #todo - update ticket user

    dict_user_by_site = get_number_user_by_site(list_hit_without_ticket)

    dict_ticket_by_site_to_create = {}
    dict_ticket_by_user_to_create = {}

    for site in dict_user_by_site:
        if(len(dict_user_by_site[site]) >= limit_hit_to_notify_site):
            dict_ticket_by_site_to_create[site] = []
    for hit in list_hit_without_ticket:
        for_site_ticket = False
        for site in dict_ticket_by_site_to_create:
            if(site in hit["url"]):
                dict_ticket_by_site_to_create[site].append(hit)
                for_site_ticket = True
                break
        if(for_site_ticket == False):
            creator = hit["createdBy"]
            if(creator == ""):
                creator = "unknown"
            try:
                dict_ticket_by_user_to_create[creator].append(hit)
            except:
                dict_ticket_by_user_to_create[creator] = [hit]

    dict_tickets = prepare_and_create_ticket(dict_ticket_by_user_to_create, "USER", dict_tickets)
    dict_tickets = prepare_and_create_ticket(dict_ticket_by_site_to_create, "SITE", dict_tickets)

def prepare_and_create_ticket(dict_data, ticket_type, dict_tickets):
    time = datetime.datetime.now()
    time = time.strftime("%Y-%m-%d")
    dict_ticket_to_create = {}
    for key_ticket in dict_data:
        dict_data_type = {}
        for hit in dict_data[key_ticket]:
            try:
                dict_data_type[hit["data_type"]].append(hit)
            except:
                dict_data_type[hit["data_type"]] = [hit]

        for info_ticket_perimeter in dict_data_type:
            info_ticket_type = ticket_type
            info_ticket_status = "NEW"
            info_ticket_id_ticket_ext = ""

            info_site_by_user = get_number_site_by_user(dict_data_type[info_ticket_perimeter])
            info_user_by_site = get_number_user_by_site(dict_data_type[info_ticket_perimeter])

            average_detection_score = 0
            for hit_for_score in dict_data_type[info_ticket_perimeter]:
                average_detection_score += int(hit_for_score["detection_score"])
            nb_hits_ticket = len(dict_data_type[info_ticket_perimeter])
            average_detection_score = int(average_detection_score / nb_hits_ticket)

            info_ticket_hit_resume = {"average_detection_score" : average_detection_score, "nb_hits" : nb_hits_ticket, "nb_concerned_users" : len(info_site_by_user), "nb_concerned_sites" : len(info_user_by_site)}
            info_ticket_hit_infos = {"concerned_users" : list(info_site_by_user.keys()), "concerned_sites" : list(info_user_by_site.keys())}
            info_ticket_hit = dict_data_type[info_ticket_perimeter]
            info_ticket_linked = ""

            info_ticket_rev = 0

            data_ticket = {"type" : info_ticket_type, "rev":info_ticket_rev, "linked_ticket" : info_ticket_linked, "perimeter" : info_ticket_perimeter, "status" : info_ticket_status, "id_ticket_ext" : info_ticket_id_ticket_ext, "hit_resume" : info_ticket_hit_resume, "hit_infos" : info_ticket_hit_infos, "hit" : info_ticket_hit}

            id_ticket = time+"_"+info_ticket_type+"_"+hashlib.sha256(json.dumps(data_ticket, indent = 4).encode('utf-8')).hexdigest()
            
            dict_ticket_to_create[id_ticket] = data_ticket
            dict_tickets[id_ticket] = data_ticket

    create_ticket(dict_ticket_to_create)
    return(dict_tickets)

def update_result_history_with_external_ticket_id():
    data_result = helper.load_last_results_from_history()
    history_file_loaded = data_result[0]
    nb_hits_loaded = len(data_result[1])
    message = f"{history_file_loaded} loaded with {nb_hits_loaded} hits"
    helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")

    data_result = data_result[1]

    dict_tickets = load_json_tickets()
    nb_ticket_loaded = len(dict_tickets)
    message = f"{nb_ticket_loaded} tickets loaded"
    helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")

    if(nb_ticket_loaded == 0):
        message = f"No ticket so exit"
        helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
        return()

    dict_external_tickets = {}
    for ticket in dict_tickets:
        id_ticket_ext = dict_tickets[ticket]["id_ticket_ext"]
        if(id_ticket_ext != ""):
            dict_external_tickets[id_ticket_ext] = []
            for hit in dict_tickets[ticket]["hit"]:
                dict_external_tickets[id_ticket_ext].append(hit["url"])

    nb_result_to_update = 0
    for id_hit in range(0, len(data_result)):
        if(data_result[id_hit]["already_notified"] == ""):
            hit_url = data_result[id_hit]["url"]
            has_external_ticket = False
            for id_ticket_ext in dict_external_tickets:
                if(hit_url in dict_external_tickets[id_ticket_ext]):
                    has_external_ticket = True
                    break
            if(has_external_ticket == True):
                data_result[id_hit]["already_notified"] = id_ticket_ext
                nb_result_to_update += 1

    if(nb_result_to_update > 0):
        message = f"{nb_result_to_update} hit(s) in result to update"
        helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
        helper.save_result(data_result, history_file_loaded)

    else:
        message = f"No hit in result to update so exit"
        helper.print_line(message, context_prepare_tickets.filename_for_helper, "INFO")
        return()

class class_context_prepare_tickets:
    def __init__(self):
        self.filename_for_helper = "prepareTickets"
        self.load_options()

    def load_options(self):
        try:
            self.option_verbosity = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "VERBOSE_LOG"))
            self.option_limit_hit_to_notify_site = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "LimitToNotifySite"))
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

context_prepare_tickets = class_context_prepare_tickets()