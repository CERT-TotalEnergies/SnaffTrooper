# -*- coding: utf-8 -*-
#!/usr/bin/python3
#author : Antoine G.

"""
TODO:
- check if GRAPH tokens still necessary
- support other authentication method
"""

import requests
import datetime
import json
import helper
import sys

def request_refresh_token(client_id, ressource, simpleName):#todo option header
    User_Agent = context_get_token.option_user_agent

    url = "https://login.microsoftonline.com/common/oauth2/devicecode?api-version=1.0"

    headers = {
        'User-Agent': User_Agent
    }

    body = {'client_id': client_id,'resource': ressource}

    r = requests.post(url, headers=headers, data = body)
    

    if(r.status_code == 200):
        json_response = r.json()
        user_code = json_response["user_code"]
        device_code = json_response["device_code"]
        verification_url = json_response["verification_url"]

        helper.print_line(f"Ask for enter device code in {verification_url}", context_get_token.filename_for_helper, "INFO")

        is_done = input(f"Please enter {user_code} in {verification_url} and confirm. (y/n) ")
        if(is_done == "y"):
            refresh_token = request_refresh_token_part2(device_code, User_Agent, client_id, "urn:ietf:params:oauth:grant-type:device_code", simpleName)
        else:
            helper.print_line(f"User do not enter the code!", context_get_token.filename_for_helper, "ERROR")
            exit()
    else:
        helper.print_line(f"When generating refresh_token phase 1", context_get_token.filename_for_helper, "ERROR")
        exit()

def request_refresh_token_part2(device_code, User_Agent, client_id, grant_type, simpleName):
    url = "https://login.microsoftonline.com/Common/oauth2/token?api-version=1.0"

    headers = {
        'User-Agent': User_Agent
    }

    body = {'client_id': client_id,'grant_type': grant_type, 'code': device_code}
    r = requests.post(url, headers=headers, data = body)
    json_response = r.json()
    base_folder = sys.argv[0][:-7]
    if(r.status_code == 200):
        json_response = r.json()
        refresh_token = json_response["refresh_token"]
        access_token = json_response["access_token"]

        with open(f"{base_folder}_data/{simpleName}_access_token.txt", "w", encoding="utf-8") as file:
            file.write(access_token)

        with open(f"{base_folder}_data/{simpleName}_refresh_token.txt", "w", encoding="utf-8") as file:
            file.write(refresh_token)

    else:
        helper.print_line(f"When generating refresh_token phase 2", context_get_token.filename_for_helper, "ERROR")

def request_access_token(User_Agent, client_id, simpleName, grant_type):
    base_folder = sys.argv[0][:-7]
    try:
        with open(f"{base_folder}_data/{simpleName}_refresh_token.txt", "r", encoding="utf-8") as file:
            refresh_token = file.read()
    except:
        helper.print_line(f"no refresh_token availabe for {simpleName}", context_get_token.filename_for_helper, "ERROR")
        return(False)

    url = "https://login.microsoftonline.com/Common/oauth2/token?api-version=1.0"
    headers = {
        'User-Agent': User_Agent
    }

    body = {'client_id': client_id,'grant_type': grant_type, 'refresh_token': refresh_token}
    r = requests.post(url, headers=headers, data = body)
    
    if(r.status_code == 200):
        json_response = r.json()
        refresh_token = json_response["refresh_token"]
        access_token = json_response["access_token"]

        with open(f"{base_folder}_data/{simpleName}_access_token.txt", "w", encoding="utf-8") as file:
            file.write(access_token)
        
        with open(f"{base_folder}_data/{simpleName}_refresh_token.txt", "w", encoding="utf-8") as file:
            file.write(refresh_token)
        #do not erase old refresh token?
        return(True)
    else:
        helper.print_line(f"When generating access_token", context_get_token.filename_for_helper, "ERROR")
        return(False)
    

def get_graph_refresh_token():
    refresh_token = request_refresh_token("9bc3ab49-b65d-410a-85ad-de819febfddc", "https://graph.microsoft.com/", "graph")

def get_graph_access_token():
    User_Agent = context_get_token.option_user_agent
    return(request_access_token(User_Agent, "9bc3ab49-b65d-410a-85ad-de819febfddc", "graph", "refresh_token"))

def get_sharepoint_refresh_token(sharepoint_targeted):
    sharepoint_targeted = sharepoint_targeted+"/"
    refresh_token = request_refresh_token("9bc3ab49-b65d-410a-85ad-de819febfddc", sharepoint_targeted, "sharepoint")

def get_sharepoint_access_token():
    User_Agent = context_get_token.option_user_agent
    return(request_access_token(User_Agent, "9bc3ab49-b65d-410a-85ad-de819febfddc", "sharepoint", "refresh_token"))

def ask_required_graph_tokens():
    if(get_graph_access_token()):
        helper.print_line(f"Graph access token loaded", context_get_token.filename_for_helper, "INFO")
    else:
        helper.print_line(f"No saved refresh token (or invalid)", context_get_token.filename_for_helper, "INFO")
        get_graph_refresh_token()

def ask_required_sharepoint_tokens(sharepoint_targeted, interactive = True):
    if(get_sharepoint_access_token()):
        helper.print_line(f"Graph access token loaded", context_get_token.filename_for_helper, "INFO")
    else:
        if(interactive == True):
            helper.print_line(f"No saved refresh token (or invalid)", context_get_token.filename_for_helper, "INFO")
            get_sharepoint_refresh_token(sharepoint_targeted)
        else:
            helper.print_line("Invalid refresh token but <INTERACTIVE> option is set to <0> for <getToken>", context_get_token.filename_for_helper, "INFO")
            exit()

def ask_required_tokens(sharepoint_targeted):
    """
    if(get_graph_access_token()):
        helper.print_line(f"Graph access tokean loaded", context_get_token.filename_for_helper, "INFO")
    else:
        helper.print_line(f"No saved refresh token (or invalid)", context_get_token.filename_for_helper, "INFO")
        get_graph_refresh_token()
    """
    if(get_sharepoint_access_token()):
        helper.print_line(f"Sharepoint access tokean loaded", context_get_token.filename_for_helper, "INFO")
    else:
        helper.print_line(f"No saved refresh token (or invalid)", context_get_token.filename_for_helper, "INFO")
        get_sharepoint_refresh_token(sharepoint_targeted)


class class_context_get_token:
    def __init__(self):
        self.filename_for_helper = "getToken"
        self.load_options()

    def load_options(self):
        try:
            self.option_user_agent = helper.get_clean_options_v2(self.filename_for_helper, specific_option = "USERAGENT")
        except Exception as e:
            helper.print_line(f"with loading of <{self.filename_for_helper}> options => **{e}**", self.filename_for_helper, "FATAL ERROR")
            exit()

context_get_token = class_context_get_token()