# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

"""
TODO:
- autocorrect path

"""

import helper
import os
import sys

def check_env():
	list_files = os.listdir(sys.argv[0][:-7])

	try:
		for sub_file in os.listdir(sys.argv[0][:-7]+"_config"):
			list_files.append("_config/"+sub_file)
	except:
		pass
	#start by _logs
	if("_logs" in list_files):
		pass
	else:
		required_folder = "_logs"
		required_folder = sys.argv[0][:-7]+required_folder
		os.mkdir(required_folder)
		message = f"Create {required_folder}: OK"
		helper.print_line(message, context_init_context.filename_for_helper, "INFO")

	verbosity = context_init_context.option_verbosity
	if(verbosity == "1"):
		helper.print_line("Check context: START", context_init_context.filename_for_helper, "INFO")
	list_required_folders = ["_data", "_results", "_result_history", "_downloaded_files_from_sharepoint", "_config/_creds", "_tickets"]
	for required_folder in list_required_folders:
		if(required_folder in list_files):
			if(verbosity == "1"):
				message = f"Check if {required_folder}: OK"
				helper.print_line(message, context_init_context.filename_for_helper, "INFO")
		else:
			required_folder = sys.argv[0][:-7]+required_folder
			os.mkdir(required_folder)
			message = f"Create {required_folder}: OK"
			helper.print_line(message, context_init_context.filename_for_helper, "INFO")
	if(verbosity == "1"):
		helper.print_line("Check context: END", context_init_context.filename_for_helper, "INFO")
	else:
		helper.print_line("Check context: OK", context_init_context.filename_for_helper, "INFO")

def check_targeted_sharepoint():
	sharepoint_targeted = helper.read_file("_config", "targeted_sharepoint.txt", write_type = "r")
	if(sharepoint_targeted == False):
		sharepoint_targeted = input("SharePoint to target: <https://XXX.sharepoint.com> ")

		if(context_init_context.option_save_targeted_sharepoint == 1):
			message = "Save SharePoint targeted to ./_config/targeted_sharepoint.txt"
			helper.print_line(message, context_init_context.filename_for_helper, "INFO")
			helper.write_file("_config", "targeted_sharepoint.txt", sharepoint_targeted, write_type = "w")
		else:
			message = "Configuration sets to not save targeted SharePoint"
			helper.print_line(message, context_init_context.filename_for_helper, "INFO")
		
	return(sharepoint_targeted)

def check_snaffler_path():
	path_snaffler = helper.read_file("_config", "path_snaffler_binary.txt", write_type = "r")
	if(path_snaffler == False):
		message = "Please be careful with '\\\\'!"
		helper.print_line(message, context_init_context.filename_for_helper, "INFO")
		path_snaffler = input("Path of Snaffler binary: <C:\\\\XXX\\\\XXX\\\\SharePointScanner\\\\_Snaffler\\\\snaffler.exe> ")

		if(context_init_context.option_save_snaffler_binary_path == 1):
			message = "Save path of Snaffler binary to ./_config/path_snaffler_binary.txt"
			helper.print_line(message, context_init_context.filename_for_helper, "INFO")
			helper.write_file("_config", "path_snaffler_binary.txt", path_snaffler, write_type = "w")
		else:
			message = "Configuration sets to not save path of Snaffler binary"
			helper.print_line(message, context_init_context.filename_for_helper, "INFO")
		
	return(path_snaffler)

class class_context_init_context:
    def __init__(self):
        self.filename_for_helper = "initContext"
        self.load_options()

    def load_options(self):
        try:
            self.option_verbosity = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "VERBOSITY"))
            self.option_save_targeted_sharepoint = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "SaveTargetedSharepoint"))
            self.option_save_snaffler_binary_path = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "SaveSnafflerBinaryPath"))
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

context_init_context = class_context_init_context()


