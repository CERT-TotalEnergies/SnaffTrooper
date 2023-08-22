# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

import csv
import os
import helper
import sys

def import_snaffpoint_processed(filepath):
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

def get_shared_folder_scanned_len(sample_line):
	calculate_shared_folder_scanned_len = 33
	while(sample_line[calculate_shared_folder_scanned_len-33:calculate_shared_folder_scanned_len] != "_downloaded_files_from_sharepoint"):
		calculate_shared_folder_scanned_len += 1
	calculate_shared_folder_scanned_len = calculate_shared_folder_scanned_len + 1
	return(calculate_shared_folder_scanned_len)

def import_snaffler(filepath, API_to_use):
	data = []

	if(API_to_use == 0):
		len_id = 37
	else:
		len_id = 35
	with open(filepath, newline='\n') as f:
		tsv_file = csv.reader(f, delimiter="\t")
		for row in tsv_file:	
			dict_data = {}
			if(len(row) == 13):
				if(context_parse_snaffler.shared_folder_scanned_len == -1):
					context_parse_snaffler.shared_folder_scanned_len = get_shared_folder_scanned_len(row[11])

				dict_data["detection_type"] = row[3]
				dict_data["detection_rule"] = row[4]
				dict_data["file_id"] = row[11][context_parse_snaffler.shared_folder_scanned_len:context_parse_snaffler.shared_folder_scanned_len+len_id-1]
				dict_data["file_name"] = row[11][context_parse_snaffler.shared_folder_scanned_len+len_id:]
				dict_data["context"] = row[12]

				data.append(dict_data)
	return(data)

def merge(data_snaffpoint, data_snaffler):
	data_merger = []
	count_merged = 0
	fields_names = data_snaffpoint[0].keys()
	for data_sp in data_snaffpoint:
		to_append = {}
		for key in fields_names:
			to_append[key] = data_sp[key]
		id_file = data_sp["id_file"]
		for data_sf in data_snaffler:
			if(data_sf["file_id"] == id_file):
				to_append["detection_type"] = data_sf["detection_type"]
				to_append["detection_rule"] = data_sf["detection_rule"]
				to_append["context"] = data_sf["context"]
				count_merged += 1
		data_merger.append(to_append)

	if(count_merged > len(data_snaffler)):
		helper.print_line("Bad count (more merged than file downloaded, maybe some double?)", "parse_snaffler", "ERROR")
	elif(count_merged < len(data_snaffler)):
		helper.print_line("Bad count", "parse_snaffler", "ERROR")#TODO investigate
	return(data_merger)


def write_results_csv(consolidated_data):
	fields_names = consolidated_data[0].keys()
	max_fields = 0
	for i in consolidated_data:
		if(len(i)>max_fields):
			max_fields = len(i)
			fields_names = i.keys()
	with open(sys.argv[0][:-7]+'_data/results_snaffpoint_snaffler.csv', "w") as file:
		writer = csv.DictWriter(file, fieldnames = fields_names)
		writer.writeheader()
		writer.writerows(consolidated_data)


class class_context_parse_snaffler:
    def __init__(self):
        self.shared_folder_scanned_len = -1
        self.filename_for_helper = "parseSnaffler"
        self.load_options()

    def load_options(self):
        try:
            pass
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

context_parse_snaffler = class_context_parse_snaffler()