# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

"""
TODO:
- snaffler_is_available not usefull anymore
"""

import os
import datetime
import subprocess, shlex
import helper
import sys

def startSnaffler(path_exe):
	snaffler_is_available = True

	verbose = context_start_snaffler.option_verbose
	path_scan_dir = "'"+context_start_snaffler.option_path_scan_dir+"'"

	if(snaffler_is_available == True):
		if(os.path.exists(path_exe)):
			snaffler_is_available = True
		else:
			snaffler_is_available = False

	if(snaffler_is_available == True):
		if(path_scan_dir != "'./_downloaded_files_from_sharepoint'"):
			list_files_to_copy = os.listdir(sys.argv[0][:-7]+"_downloaded_files_from_sharepoint")
			for file in list_files_to_copy:
				if(verbose == 1):
					message = f"Copy: {file}"
					helper.print_line(message, context_start_snaffler.filename_for_helper, "INFO")
				path_file_to_open = sys.argv[0][:-7]+"_downloaded_files_from_sharepoint/"+str(file)
				with open(path_file_to_open, "rb") as fileToCopy:
					content_fileToCopy = fileToCopy.read()

				path_file_to_open = path_scan_dir+"/"+str(file)
				with open(path_file_to_open, "wb") as fileToWrite:
					fileToWrite.write(content_fileToCopy)
			message = "Copy downloaded files to Snaffler scan folder"
			helper.print_line(message, context_start_snaffler.filename_for_helper, "INFO")

		output_file = "'"+os.getcwd()+"/_data/resultsSnaffler.txt"+"'"
		if(verbose == 0):
			command_to_execute = f"{path_exe} -y -o {output_file} -i {path_scan_dir}"
		else:
			command_to_execute = f"{path_exe} -s -y -o {output_file} -i {path_scan_dir}"
		
		message = f"Execute: {command_to_execute}"
		helper.print_line(message, context_start_snaffler.filename_for_helper, "INFO")
		subprocess.run(shlex.split(command_to_execute))

		if(path_scan_dir != "'./_downloaded_files_from_sharepoint'"):
			message = "Remove copy of downloaded files to Snaffler scan folder"
			helper.print_line(message, context_start_snaffler.filename_for_helper, "INFO")
			list_copied_files = os.listdir(path_scan_dir)
			for file in list_copied_files:
				file_to_delete = path_scan_dir+"/"+file
				if(verbose == 1):
					message = f"Remove: {file_to_delete}"
					helper.print_line(message, context_start_snaffler.filename_for_helper, "INFO")
				os.remove(file_to_delete)
		return(True)
	else:
		return(False)
	
class class_context_start_snaffler:
    def __init__(self):
        self.filename_for_helper = "startSnaffler"
        self.load_options()

    def load_options(self):
        try:
            self.option_path_scan_dir = helper.get_clean_options_v2(self.filename_for_helper, specific_option = "ScanPathSnaffler")
            self.option_verbose = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "VERBOSE"))
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

context_start_snaffler = class_context_start_snaffler()