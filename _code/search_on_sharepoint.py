# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

"""
TODO:
- in "createSearchQueryNoFQL" check row limit operation
- in "parseResultSharePoint" how to get more than 500 hits?
- in "parseResultSharePoint" understand the amout of hit by result
- refactor and check everything here
- add option to remove downloaded files if not present anymore
"""

from pprint import pprint as ppt
import requests
import csv
import datetime
import os
import xml.etree.ElementTree as ET
import helper_sharepoint
import helper
import sys

def load_presets():
	list_presets = os.listdir(sys.argv[0][:-7]+"_config/_presets_SnaffPoint")
	dict_preset = {}
	for preset in list_presets:
		tree_preset = ET.parse(sys.argv[0][:-7]+"_config/_presets_SnaffPoint/"+preset)
		root_preset = tree_preset.getroot()
		dict_preset[root_preset[0].text] = {}
		for child in root_preset[1]:
			if(child.tag == "QueryText"):
				queryText = child.text
			elif(child.tag == "EnableFql"):
				EnableFql = child.text
			elif(child.tag == "RefinementFilters"):
				RefinementFilters = child.text
			elif(child.tag == "SortList"):
				SortList = child.text

		dict_preset[root_preset[0].text]["queryText"] = queryText
		dict_preset[root_preset[0].text]["EnableFql"] = EnableFql
		dict_preset[root_preset[0].text]["SortList"] = SortList
		dict_preset[root_preset[0].text]["RefinementFilters"] = RefinementFilters

		list_to_encode = ["queryText", "EnableFql", "SortList", "RefinementFilters"]
		for key_encode in list_to_encode:
			dict_preset[root_preset[0].text][key_encode] = dict_preset[root_preset[0].text][key_encode].replace('"', "%22")
			dict_preset[root_preset[0].text][key_encode] = dict_preset[root_preset[0].text][key_encode].replace(',', "%2c")
			dict_preset[root_preset[0].text][key_encode] = dict_preset[root_preset[0].text][key_encode].replace('=', "%3d")
			dict_preset[root_preset[0].text][key_encode] = dict_preset[root_preset[0].text][key_encode].replace(':', "%3a")

	return(dict_preset) 

def createSearchQueryNoFQL(dict_preset, currentRow, maxRows=500):
	for preset in dict_preset:#REPLACE the filter by one working on OnPremise version
		RefinementFilter = dict_preset[preset]["RefinementFilters"]
		dict_preset[preset]["RefinementFilters"] = RefinementFilter.replace("filetype", "fileExtension")
		if(currentRow == 0):
			query = "query?querytext='"+dict_preset[preset]["queryText"]+"'"+"&rowlimit="+str(maxRows)+"&refinementfilters='"+dict_preset[preset]["RefinementFilters"]+"'&sortlist='"+dict_preset[preset]["SortList"]+"'"
		else:
			query = "query?querytext='"+dict_preset[preset]["queryText"]+"'"+"&rowlimit="+str(maxRows)+"&refinementfilters='"+dict_preset[preset]["RefinementFilters"]+"'&sortlist='"+dict_preset[preset]["SortList"]+"'&startrow="+str(currentRow)
			
		dict_preset[preset]["query"] = query

	return(dict_preset)

def createSearchQuery(dict_preset, currentRow, maxRows=500):
	for preset in dict_preset:
		if(currentRow == 0):
			query = "query?querytext='"+dict_preset[preset]["queryText"]+"'&enablefql="+dict_preset[preset]["EnableFql"]+"&rowlimit="+str(maxRows)+"&refinementfilters='"+dict_preset[preset]["RefinementFilters"]+"'&sortlist='"+dict_preset[preset]["SortList"]+"'"
		else:
			query = "query?querytext='"+dict_preset[preset]["queryText"]+"'&enablefql="+dict_preset[preset]["EnableFql"]+"&rowlimit="+str(maxRows)+"&refinementfilters='"+dict_preset[preset]["RefinementFilters"]+"'&sortlist='"+dict_preset[preset]["SortList"]+"'&startrow="+str(currentRow)
		
		dict_preset[preset]["query"] = query
	return(dict_preset)

def searchOnSharepoint(dict_preset_with_query, sharepointUrl, max_row_by_query=500):
	base_url = sharepointUrl+"/_api/search/"
	dict_url_recovered = []
	for key in dict_preset_with_query:
		number_of_url_parsed = 0
		safe_while = max_row_by_query*(-1)
		continue_while = True

		list_url_by_key = []
		message = f"Search for: {key}"
		helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")
		url_f = base_url+dict_preset_with_query[key]["query"]

		response = helper_sharepoint.make_request(url_f, sharepointUrl)
		data_parsed = parseResultSharePoint(response, sharepointUrl)

		number_of_results = int(data_parsed[1])
		number_of_url_parsed += int(data_parsed[2])
		list_url_by_key.extend(data_parsed[0])

		message = f"Number of hit(s) for {key}: {number_of_results}"
		helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")
		message = f"Number of recoverd URL for {key}: {number_of_url_parsed}"
		helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")

		while(number_of_url_parsed < number_of_results and continue_while == True):
			url_f_row = url_f+"&startrow="+str(number_of_url_parsed)
			response = helper_sharepoint.make_request(url_f_row, sharepointUrl)
			data_parsed = parseResultSharePoint(response, sharepointUrl)
			number_of_results = int(data_parsed[1])
			number_of_url_parsed += int(data_parsed[2])
			list_url_by_key.extend(data_parsed[0])
			safe_while += max_row_by_query
			message = f"Number of recoverd URL for {key}: {number_of_url_parsed}"
			helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")
			if(safe_while > number_of_results):
				continue_while = False
				message = f"ERROR: Emergency exit of searchOnSharepoint for {key}"
				helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")

		if(number_of_results != number_of_url_parsed):
			message = f"ERROR: {number_of_results} hits but only {number_of_url_parsed} URLs revovered"
			helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")
				
		data_type = "FromSharePoint:"+sharepointUrl
		for url in list_url_by_key:
			dict_url_recovered.append({"source_type":key, "url":url, "data_type":data_type})

	return(dict_url_recovered)

def searchOnSharepointOnPremise(dict_preset_with_query, sharepointUrl, max_row_by_query=500):#SharePoint limit 500 rows
	base_url = sharepointUrl+"/_api/search/"
	dict_url_recovered = []
	for key in dict_preset_with_query:
		if("_NO-ON-PREM" in key):
			message = f"No search for {key} because on-premise search"
			helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")
		else:
			number_of_url_parsed = 0
			safe_while = max_row_by_query*(-1)
			continue_while = True

			list_url_by_key = []

			message = f"Search for: {key}"
			helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")
			url_f = base_url+dict_preset_with_query[key]["query"]

			response = helper_sharepoint.make_request(url_f, sharepointUrl)

			data_parsed = parseResultSharePointOnPremise(response, sharepointUrl)

			number_of_results = int(data_parsed[1])
			number_of_url_parsed += int(data_parsed[2])
			list_url_by_key.extend(data_parsed[0])

			message = f"Number of hit(s) for {key}: {number_of_results}"
			helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")

			message = f"Number of recoverd URL for {key}: {number_of_url_parsed}"
			helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")

			while(number_of_url_parsed < number_of_results and continue_while == True):
				url_f_row = url_f+"&startrow="+str(number_of_url_parsed)
				response = helper_sharepoint.make_request(url_f_row, sharepointUrl)
				data_parsed = parseResultSharePointOnPremise(response, sharepointUrl)
				number_of_results = int(data_parsed[1])
				number_of_url_parsed += int(data_parsed[2])
				list_url_by_key.extend(data_parsed[0])
				safe_while += max_row_by_query
				message = f"Number of recoverd URL for {key}: {number_of_url_parsed}"
				helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")
				if(safe_while > number_of_results):
					continue_while = False
					message = f"ERROR: Emergency exit of searchOnSharepoint for {key}"
					helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")

			if(number_of_results != number_of_url_parsed):
				message = f"ERROR: {number_of_results} hits but only {number_of_url_parsed} URLs revovered"
				helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")

			data_type = "FromSharePoint:"+sharepointUrl
			for url in list_url_by_key:
				dict_url_recovered.append({"source_type":key, "url":url, "data_type":data_type})

	return(dict_url_recovered)

def write_results_csv(consolidated_data):
	message = "Write to CSV"
	helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")
	try:
		fields_names = consolidated_data[0].keys()
		with open(sys.argv[0][:-7]+'_data/results_search_on_sharepoint.csv', "w", encoding="utf-8") as file:
			writer = csv.DictWriter(file, fieldnames = fields_names)
			writer.writeheader()
			writer.writerows(consolidated_data)
	except:
		message = "No data to save to CSV!"
		helper.print_line(message, context_search_on_sharepoint.filename_for_helper, "INFO")


def parseResultSharePoint(response, sharepointUrl):
	list_url_result = []
	result_total_rows = response.get("d", {}).get("query", {}).get("PrimaryQueryResult", {}).get("RelevantResults", {}).get("TotalRows")
	result_row_obtained = response.get("d", {}).get("query", {}).get("PrimaryQueryResult", {}).get("RelevantResults", {}).get("RowCount")

	interesting_part = (response.get("d", {}).get("query", {}).get("PrimaryQueryResult", {}).get("RelevantResults", {}).get("Table", {}).get("Rows", {}).get("results", {}))
	
	for sub_interesting_part in interesting_part:
		count_potential_url = 0
		list_potential_url = []
		for item in sub_interesting_part["Cells"]["results"]:
			if(item["ValueType"] == "Edm.String"):
				if(sharepointUrl in item["Value"]):
					list_potential_url.append(item["Value"])

					count_potential_url += 1#TODO why so many?
		if(len(list_potential_url)>0):
			list_url_result.append(list_potential_url[-1])

	return([list_url_result, result_total_rows, result_row_obtained])

def parseResultSharePointOnPremise(response, sharepointUrl):
	list_url_result = []
	result_total_rows = response.get("d", {}).get("query", {}).get("PrimaryQueryResult", {}).get("RelevantResults", {}).get("TotalRows")
	result_row_obtained = response.get("d", {}).get("query", {}).get("PrimaryQueryResult", {}).get("RelevantResults", {}).get("RowCount")

	interesting_part = (response.get("d", {}).get("query", {}).get("PrimaryQueryResult", {}).get("RelevantResults", {}).get("Table", {}).get("Rows", {}).get("results", {}))
	
	try:#Because on premise use several subsites
		splitted_sharepoint_url = sharepointUrl.split(".")
		sharepointUrl_n = splitted_sharepoint_url[1]
		for part_sharepoint_url in splitted_sharepoint_url[2:]:
			sharepointUrl_n = sharepointUrl_n + "." + part_sharepoint_url
		sharepointUrl = sharepointUrl_n
	except:
		pass
	
	for sub_interesting_part in interesting_part:
		count_potential_url = 0
		list_potential_url = []
		for item in sub_interesting_part["Cells"]["results"]:
			if(item["ValueType"] == "Edm.String"):
				if(sharepointUrl in item["Value"]):
					list_potential_url.append(item["Value"])
					count_potential_url += 1
		if(len(list_potential_url)>0):
			list_url_result.append(list_potential_url[-1])

	return([list_url_result, result_total_rows, result_row_obtained])

class class_context_search_on_sharepoint:
    def __init__(self):
        self.filename_for_helper = "searchOnSharepoint"
        self.load_options()

    def load_options(self):
        try:
            pass
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

context_search_on_sharepoint = class_context_search_on_sharepoint()