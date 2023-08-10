# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

"""
TODO:
- in "get_info_of_SharePoint_file_from_url" user better ID than email
- in "get_author_property" limit the information collected
- in "collect" write the result to a file
"""

import helper
import helper_sharepoint
from pprint import pprint as ppt
import csv
import sys

def get_info_of_SharePoint_file_from_url(SharePoint_file_url, sharepoint_targeted):
    print(SharePoint_file_url)
    splitted_url = SharePoint_file_url.split("/")
    SharePoint_url = "https://"+splitted_url[2]
    context_url = SharePoint_url + "/" + splitted_url[3] + "/" + splitted_url[4]
    property_to_search = context_study_sharepoint_url.property_to_search

    search_options = "?$select=Author,ModifiedBy,Name,TimeCreated,TimeLastModified,Length,ETag&$expand=Author/ID&$expand=ModifiedBy"

    file_relative_url = ""
    for relative_url_part in splitted_url[3:]:
        file_relative_url = file_relative_url + "/" + relative_url_part

    search_url = context_url + "/_api/web/getFileByServerRelativeUrl('"+file_relative_url+"')"+search_options
    try:
        data = helper_sharepoint.make_request(search_url, sharepoint_targeted)
    except:
        pass#if connection error
    
    url = SharePoint_file_url

    name = ""
    etag = ""
    createdDateTime = ""
    lastModifiedDateTime = ""
    size = ""
    file_status = ""

    try:
        name = data["d"]["Name"]
        etag = data["d"]["ETag"][2:38]
        createdDateTime = data["d"]["TimeCreated"]
        lastModifiedDateTime = data["d"]["TimeLastModified"]
        size = data["d"]["Length"]
        file_status = "InfoGathered"
    except:
        file_status = "InfoGatheringError"

    try:
        author_UPN = data["d"]["Author"]["UserPrincipalName"]
    except:
        author_UPN = None
    try:
        modifiedBy_UPN = data["d"]["ModifiedBy"]["UserPrincipalName"]
    except:
        modifiedBy_UPN = None

    if(property_to_search != "None"):
        author_info = get_author_property(author_UPN, modifiedBy_UPN, SharePoint_url, property_to_search, sharepoint_targeted)
        if(author_info == False):
            author_department = ""
            author_UPN = ""
        else:
            author_department = author_info[0]
            author_UPN = author_info[1]

    dict_info_from_url = {}
    dict_info_from_url["url"] = url
    dict_info_from_url["name"] = name
    dict_info_from_url["id_file"] = etag
    dict_info_from_url["createdDateTime"] = createdDateTime
    dict_info_from_url["lastModifiedDateTime"] = lastModifiedDateTime
    dict_info_from_url["size"] = size
    dict_info_from_url["createdBy"] = author_UPN
    dict_info_from_url["createdBy_dpt"] = author_department
    dict_info_from_url["file_status"] = file_status

    return(dict_info_from_url)

def get_author_property(author_UPN, modifiedBy_UPN, SharePoint_url, property_to_search, sharepoint_targeted):
    upn_to_check = None
    if(author_UPN != modifiedBy_UPN):#TODO: check if still usefull
        if(author_UPN == None):
            upn_to_check = modifiedBy_UPN
        else:
            upn_to_check = author_UPN
    else:
        upn_to_check = author_UPN

    if(upn_to_check != None):#TODO
        search_url = SharePoint_url + "/sites/PAR_IE/_api/SP.UserProfiles.PeopleManager/GetPropertiesFor(accountName=@v)?@v=%27i:0%23.f|membership|"+upn_to_check+"%27"
        data = helper_sharepoint.make_request(search_url, sharepoint_targeted)
        try:
            for user_property in data["d"]["UserProfileProperties"]["results"]:
                if(user_property["Key"] == property_to_search):
                    return([user_property["Value"], author_UPN])
            return(False)
        except:
            return(["", author_UPN])
    else:
        return(False)

def download_file_by_url(SharePoint_file_url, etag, filename, sharepoint_targeted):
    splitted_url = SharePoint_file_url.split("/")
    SharePoint_url = "https://"+splitted_url[2]
    context_url = SharePoint_url + "/" + splitted_url[3] + "/" + splitted_url[4]
    file_relative_url = ""
    for relative_url_part in splitted_url[3:]:
        file_relative_url = file_relative_url + "/" + relative_url_part
    download_url = context_url + "/_api/web/getFileByServerRelativeUrl('"+file_relative_url+"')"+"/$value"
    file_content = helper_sharepoint.make_request(download_url, sharepoint_targeted, '*')
    filename_with_etag = etag+"_"+filename
    return(helper.write_file(context_study_sharepoint_url.folder_save_downloaded_files, filename_with_etag, file_content))

def read_result_search_on_sharepoint(result_search_on_sharepoint_path):
    data = []
    with open(result_search_on_sharepoint_path, newline='\n', encoding="utf-8") as f:
        reader = csv.reader(f)
        temp_rows = []
        for row in reader:
            temp_rows.append(row)

    for row in temp_rows[1:]:
        temp_dict = {}
        id_key = 0
        for key in temp_rows[0]:
            temp_dict[key] = row[id_key]
            id_key += 1
        
        data.append(temp_dict)
    return(data)

def collect(sharepoint_targeted):
    dict_stats = {"nb_download_tooBig" : 0, "nb_missing_UPN" : 0, "nb_missing_dpt" : 0, "nb_downloaded" : 0, "nb_download_error" : 0, "nb_try_info_gathering" : 0, "nb_info_gathered" : 0, "nb_info_gathering_error" : 0, "nb_already_downloaded" : 0}
    try:
        with open(sys.argv[0][:-7]+"_data/save_consolidated_data_d2.obj", "rb") as file_consolidated_data:
            saved_tmp_data = pickle.load(file_consolidated_data)
            consolidated_data = saved_tmp_data[0]
            dict_stats = saved_tmp_data[1]
            message = f"Load data from previous session"
            number_to_study = len(consolidated_data)
            helper.print_line(message, context_study_sharepoint_url.filename_for_helper, "INFO")
    except:
        result_search_on_sharepoint_path = sys.argv[0][:-7]+"_data/results_search_on_sharepoint.csv"
        list_extracted_data = read_result_search_on_sharepoint(result_search_on_sharepoint_path)
        consolidated_data = []

        number_to_study = len(list_extracted_data)
        message = f"{number_to_study} URL to check!"
        helper.print_line(message, context_study_sharepoint_url.filename_for_helper, "INFO")

        counter = 0
        for dict_data in list_extracted_data:
            dict_stats["nb_try_info_gathering"] += 1
            temp_dict = get_info_of_SharePoint_file_from_url(dict_data["url"], sharepoint_targeted)
            temp_dict["data_type"] = dict_data["data_type"]
            temp_dict["source_type"] = dict_data["source_type"]
            if(temp_dict["file_status"] == "InfoGathered"):
                dict_stats["nb_info_gathered"] += 1
            else:
                dict_stats["nb_info_gathering_error"] += 1

            if(temp_dict["createdBy"] == ""):
                dict_stats["nb_missing_UPN"] += 1
                if(temp_dict["createdBy_dpt"] == ""):
                    dict_stats["nb_missing_dpt"] += 1
            consolidated_data.append(temp_dict)
            counter += 1
            helper.manage_stats(dict_stats, counter, number_to_study, "InfoGatheringFromSharePoint")

        try:
            with open(sys.argv[0][:-7]+"_data/save_consolidated_data_d2.obj", "wb") as file_consolidated_data:
                pickle.dump([consolidated_data, dict_stats], file_consolidated_data)
                os.rename(sys.argv[0][:-7]+"_data/save_consolidated_data_d2.obj", sys.argv[0][:-7]+"_data/save_consolidated_data_d2_bkp.obj")
        except:
            message = "cannot save with pickle"
            helper.print_line(message, context_study_sharepoint_url.filename_for_helper, "ERROR")

    message = "End of data collection, start download"
    helper.print_line(message, context_study_sharepoint_url.filename_for_helper, "INFO")


    MaxSizeForDownload = context_study_sharepoint_url.max_size_for_download
    list_id_file_downloaded_from_sharepoint = helper.get_list_already_downloaded()

    for counter in range(0, len(consolidated_data)):
        if(consolidated_data[counter]["file_status"] == "InfoGathered"):
            if(consolidated_data[counter]["id_file"] in list_id_file_downloaded_from_sharepoint):
                dict_stats["nb_already_downloaded"] += 1
                consolidated_data[counter]["file_status"] = "Downloaded"
            else:
                if(int(consolidated_data[counter]["size"]) < MaxSizeForDownload):
                    url = consolidated_data[counter]["url"]
                    if(download_file_by_url(consolidated_data[counter]["url"], consolidated_data[counter]["id_file"], consolidated_data[counter]["name"], sharepoint_targeted)):
                        consolidated_data[counter]["file_status"] = "Downloaded"
                        message = f"Download {url}"
                        dict_stats["nb_downloaded"] += 1
                        helper.print_line(message, context_study_sharepoint_url.filename_for_helper, "INFO")
                    else:
                        consolidated_data[counter]["file_status"] = "DownloadError"
                        message = f"with {url}"
                        dict_stats["nb_download_error"] += 1
                        helper.print_line(message, context_study_sharepoint_url.filename_for_helper, "ERROR")
                else:
                    consolidated_data[counter]["file_status"] = "TooBig"
                    dict_stats["nb_download_tooBig"] += 1
        helper.manage_stats(dict_stats, counter, number_to_study, "DownloadFromSharePoint")

    if(helper.manage_stats(dict_stats, counter, number_to_study, "StatInfoFromSharePointApi", save_it = True)):
        message = f"Write SharePoint data extraction stats: OK"      
        helper.print_line(message, context_study_sharepoint_url.filename_for_helper, "INFO")
    else:
        message = f"with write SharePoint data extraction stats"      
        helper.print_line(message, context_study_sharepoint_url.filename_for_helper, "ERROR")

    if(helper.write_results_csv(consolidated_data, "results_snaff.csv", "_data")):
        message = f"SharePoint data extraction: OK"      
        helper.print_line(message, context_study_sharepoint_url.filename_for_helper, "INFO")
    else:
        message = f"when writing results_snaff.csv" 
        helper.print_line(message, context_study_sharepoint_url.filename_for_helper, "ERROR")

    #TODO

class class_context_study_sharepoint_url:
    def __init__(self):
        self.filename_for_helper = "studySharepointUrl"
        self.folder_save_downloaded_files = "_downloaded_files_from_sharepoint"
        self.load_options()

    def load_options(self):
        try:
            self.property_to_search = helper.get_clean_options_v2(self.filename_for_helper, specific_option = "SpecificProperty")
            self.max_size_for_download = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "MaxSizeForDownload"))
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()
            
context_study_sharepoint_url = class_context_study_sharepoint_url()