# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

"""
TODO: check if invalid regex can cause bug
"""

import csv
import re
import requests
import datetime
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

def check_if_snaffler(data):
	apply_regex = True
	time_day = datetime.datetime.now()
	time_day = time_day.strftime("%Y:%m:%d")
	list_regex = []
	try:
		with open(sys.argv[0][:-7]+"_config/specific_regex.txt", "r") as file_regex:
			for line in file_regex:
				list_regex.append(line[:-1])
	except:
		apply_regex = False
		message = f"No regex search since <./_config/specific_regex.txt> is not present"
		helper.print_line(message, "add_regex", "INFO")

	if(apply_regex == True):
		count_added_detect = 0
		count_added_precision = 0
		dict_not_check = {}
		count = 0
		for info in data:
			try:
				info["detection_type"]
			except:
				info["detection_type"] = ""

			if(info["detection_type"] == ""):
				if(info["file_status"] == "Downloaded"):
					regex_result = use_specific_regex(info["id_file"], info["name"], list_regex)
					if(regex_result == "NoRegexCauseBinary"):
						data[count]["detection_type"] = "NoRegexCauseBinary"
					elif(regex_result == "RegexNoHit"):
						data[count]["detection_type"] = "RegexNoHit"
					else:
						data[count]["detection_type"] = "RegexHit"
						data[count]["context"] = regex_result
						count_added_detect += 1
			elif(info["detection_type"] != ""):
				if(info["file_status"] == "Downloaded"):
					regex_result = use_specific_regex(info["id_file"], info["name"], list_regex)
					if(regex_result == "NoRegexCauseBinary"):
						data[count]["detection_type"] = data[count]["detection_type"]+" - "+"NoRegexCauseBinary"
					elif(regex_result == "RegexNoHit"):
						data[count]["detection_type"] = data[count]["detection_type"]+" - "+"RegexNoHit"
					else:
						data[count]["detection_type"] = data[count]["detection_type"]+" - "+"RegexHit"
						count_added_precision += 1
			try:
				data[count]["first_scan_detection_date"]
			except:
				data[count]["first_scan_detection_date"] = time_day
			count += 1
		message = f"Added results with regex without Snaffler hit: {count_added_detect}"
		helper.print_line(message, "add_regex", "INFO")
		message = f"Added results with regex with Snaffler hit: {count_added_precision}"
		helper.print_line(message, "add_regex", "INFO")
	return(data)

def use_specific_regex(id_file, filename, regex_list):
	base_folder = sys.argv[0][:-7]
	filepath = f"{base_folder}_downloaded_files_from_sharepoint/{id_file}_{filename}"
	file_to_study = open(filepath, "r")
	try:
		file_content = file_to_study.read()
	except:
		return("NoRegexCauseBinary")
		file_to_study.close()
	list_match = []
	list_matched_regex = []
	context = ""
	for regex in regex_list:
		pattern = re.compile(regex)
		for match in re.finditer(pattern, filename):
			context += "*** REGEX in filename ***"
			break
		for match in re.finditer(pattern, file_content):
			list_match.append(match)
			list_matched_regex.append(regex)

	id_match = 0
	if(len(list_match)>0):
		context = ""
		for match in list_match:

			start_ = match.span()[0]
			stop_ = match.span()[1]
			if(start_-50<0):
				start_ = 0
			if(stop_+50>len(file_content)-1):
				stop_=len(file_content)

			context = context + " [" + list_matched_regex[id_match] + " ] "
			context += file_content[start_-context_add_regex.option_size_context:stop_+context_add_regex.option_size_context]
			context = context.replace("\n", "x")
			context = context.replace(",", "x")
			id_match += 1
		if(len(context) > context_add_regex.option_total_size_context):
			context = context[0:context_add_regex.option_total_size_context]#limitation in case of too many hits in one file
		return(context)
	else:
		return("RegexNoHit")

def write_results_csv(consolidated_data):
	fields_names = consolidated_data[0].keys()
	max_fields = 0
	for i in consolidated_data:
		if(len(i)>max_fields):
			max_fields = len(i)
			fields_names = i.keys()
	with open(sys.argv[0][:-7]+'_data/results_snaffpoint_snaffler_regex.csv', "w") as file:
		writer = csv.DictWriter(file, fieldnames = fields_names)
		writer.writeheader()
		writer.writerows(consolidated_data)

class class_context_add_regex:
    def __init__(self):
        self.filename_for_helper = "addRegex"
        self.load_options()

    def load_options(self):
        try:
            self.option_size_context = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "SizeContextRegex"))#begin and after
            self.option_total_size_context = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "TotalSizeContext"))
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

context_add_regex = class_context_add_regex()


