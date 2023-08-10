# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

"""
WARNING: SSL certificate is not check!

TODO:
- Optimization possible by checking whether a previous access token exists, rather than regenerating one in "get_access_token"

"""

import requests
import get_token
import helper
import get_token_sharepoint_on_premise
import sys

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_access_token(sharepoint_targeted):
    get_token.ask_required_sharepoint_tokens(sharepoint_targeted, context_helper_sharepoint.option_interactive)

    with open(sys.argv[0][:-7]+"_data/sharepoint_access_token.txt", "r", encoding="utf-8") as file_access_token:
        context_helper_sharepoint.access_token = file_access_token.readline()
        if(context_helper_sharepoint.access_token[-1] == "\n"):
            context_helper_sharepoint.access_token = context_helper_sharepoint.access_token[:-1]

def sub_make_request(url, content_type):
    headers = {
        'Authorization': 'Bearer {}'.format(context_helper_sharepoint.access_token),
        'Accept': content_type
    }
    r = requests.get(url, headers=headers)
    return(r)

def sub_make_request_on_premise(url, content_type):
    headers = {
        'Accept': content_type
    }
    r = requests.get(url, headers=headers, auth=get_token_sharepoint_on_premise.get_on_premise_token(), verify=False)
    return(r)

def make_request(url, sharepoint_targeted, content_type = 'application/json;odata=verbose;charset=utf-8'):
    if(context_helper_sharepoint.is_on_premise == None):
        if(helper.read_file("_data", "IsOnePrem.txt", write_type = "r") == "1"):
            context_helper_sharepoint.is_on_premise = True
        else:
            context_helper_sharepoint.is_on_premise = False

    if(context_helper_sharepoint.access_token == None and context_helper_sharepoint.is_on_premise == False):
        get_access_token(sharepoint_targeted)

    if(context_helper_sharepoint.is_on_premise == False):
        r = sub_make_request(url, content_type)
    else:
        r = sub_make_request_on_premise(url, content_type)

    if(r.status_code == 401 and context_helper_sharepoint.is_on_premise == False):
        helper.print_line("invalid token!", context_helper_sharepoint.filename_for_helper, "ERROR")
        get_token.ask_required_sharepoint_tokens(sharepoint_targeted, context_helper_sharepoint.option_interactive)
        r = sub_make_request(url, content_type)
            
        if(r.status_code == 401):
            helper.print_line("New refresh token generated but still 401 error", context_helper_sharepoint.filename_for_helper, "FATAL ERROR")
            exit()
    if(r.status_code == 401 and context_helper_sharepoint.is_on_premise == True):
        helper.print_line("NTLM authentication failed.", context_helper_sharepoint.filename_for_helper, "FATAL ERROR")
        #exit()
    try:
        if(content_type == 'application/json;odata=verbose;charset=utf-8'):
            return r.json()
        else:
            return(r.content)
    except:
        message = f"Response is not json for <{url}>!"
        helper.print_line(message, context_helper_sharepoint.filename_for_helper, "FATAL ERROR")
        exit()

class class_context_helper_sharepoint:
    def __init__(self):
        self.access_token = None
        self.is_on_premise = None
        self.filename_for_helper = "helperSharePoint"
        self.load_options()

    def load_options(self):
        try:
            self.option_interactive = bool(helper.get_clean_options_v2(self.filename_for_helper, specific_option = "INTERACTIVE"))
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

context_helper_sharepoint = class_context_helper_sharepoint()