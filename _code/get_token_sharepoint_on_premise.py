# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

"""
WARNING: SSL certificate is not check!
"""

import requests
import datetime
import json
import helper
from requests_ntlm import HttpNtlmAuth
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_on_premise_token():
    if(context_get_token_sharepoint_on_premise.NTLM_creds == None):
        saved_user = helper.read_file("_config/_creds", "NTLM_user.txt", write_type = "r")
        saved_password = helper.read_file("_config/_creds", "NTLM_password.txt", write_type = "r")
        if(saved_user != False and saved_password !=False):
            helper.print_line("Load saved NTLM credentials", context_get_token_sharepoint_on_premise.filename_for_helper, "INFO")

        else:
            helper.print_line("No NTLM credentials saved. Ask for credentials!", context_get_token_sharepoint_on_premise.filename_for_helper, "INFO")
            domain = input("Domain: ")
            saved_user = input("Username: ")
            saved_user = domain+"\\"+saved_user
            saved_password = input("Password: ")

            if(context_get_token_sharepoint_on_premise.option_save_ntlm_creds == 1):
                helper.print_line("Save NTLM credentials in ./_config/_creds/NTLM_*.txt", context_get_token_sharepoint_on_premise.filename_for_helper, "INFO")
                helper.write_file("_config/_creds", "NTLM_user.txt", saved_user, write_type = "w")
                helper.write_file("_config/_creds", "NTLM_password.txt", saved_password, write_type = "w")
            else:
                helper.print_line("Configuration sets to not save NTLM credentials", context_get_token_sharepoint_on_premise.filename_for_helper, "INFO")
        context_get_token_sharepoint_on_premise.NTLM_creds = [saved_user, saved_password]

    return(HttpNtlmAuth(context_get_token_sharepoint_on_premise.NTLM_creds[0], context_get_token_sharepoint_on_premise.NTLM_creds[1]))

class class_context_get_token_sharepoint_on_premise:
    def __init__(self):
        self.NTLM_creds = None
        self.filename_for_helper = "getTokenOnPremise"
        self.load_options()

    def load_options(self):
        try:
            self.option_save_ntlm_creds = int(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "SaveNTLMCreds"))
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

context_get_token_sharepoint_on_premise = class_context_get_token_sharepoint_on_premise()