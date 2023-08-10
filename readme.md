SnaffTrooper
=

Readme TLDR
-

Search on SharePoint and save result in "./results" : **./main.py --start**

Purpose of this project
-
This project is designed to search secrets on SharePoint (online and on premise) and simplify remediation with keeping an history of the results.
It also enables to create .json ticket to easily import them in your favorite case management tool.
A web interface is avaible to process false positive.

Basically this tool:
* search secrets on SharePoint using the filters set in "./\_config/\_presets_SnaffPoint"
* download the files identified
* use Snaffler to add context to the downloaded files
* use custom regex to add context to the downloaded files
* calculate a detection score to prioritize the remediation
* create json-formated ticket to import the results in a case management tool

Warning
-

* This code is still in beta.
* This code was mainly tested on a Windows environment.
* This code interacts with file system and Microsoft API...
* This code should raise security alerts.
* This tool download files! Please ensure that you enough space.

Major options
-
* `--start` - start `--extraction` and `--processing`
* `--extraction` - scan and extract data of the specified SharePoint in configuration file or interactively
* `--processing` - process the data gathered with `--extraction` and create result file
* `--manual_processing` - expose a WEB application to manually indicate of the hits contained in the result file are true or false positive
* `--tickets` - create tickets from hit(s) contained in result file, if "options.txt" `main - OnlyManual` is set to "1", only hit with **manual_status** set with `--manual_processing` will be processed

Configuration files (./\_config)
-
* ./\_config/options.txt: _part of the project_ 
	* please take a look at the file contents
* ./\_config/\_creds: _automatic creation at first launch_
	* contains "NTLM_password.txt" and "NTLM_password.txt" if "options.txt" `getTokenOnPremise - SaveNTLMCreds` is set to "1" and an on premise SharePoint has been scanned
	* to avoid operator interaction in case of scanning on premise SharePoint, just create and complete the two files before to start the scan
* ./\_config/\_presets_SnaffPoint: _part of the project_
	* contains the presets of the [SnaffPoint project](https://github.com/nheiniger/SnaffPoint) of [Nicolas Heiniger](https://github.com/nheiniger) (with some modifications for on-premise search)
* ./\_config/dict_score.json: _automatic creation at first launch_ 
	* used by "archive_results.py" to calculate the **detection_score**
	* to change detection score, just modify it and start a scan (detection score of previous result will be updated)
* ./\_config/excluded_hits.txt: _manual creation_ - used to exclude hit from manual validation or ticket creation
	* **LINE EXAMPLE:** `name = *.plop` exclude all hit with **name** ending with ".plop"
	* **LINE EXAMPLE:** `name = *!NOCONTENT!*` exclude all hit with **name** without content
	* **LINE EXAMPLE:** `file_status = InfoGatheringError` exclude all hit where **file_status** is "InfoGatheringError"
	* **LINE EXAMPLE:** `still_present = 0` exclude all hit where **still_present** is equal "0"
	* **LINE EXAMPLE:** `detection_score = 10` exclude all hit where **detection_score** is equal to "10"
* ./\_config/excluded_sites.txt: _manual creation_ - used to exclude hit from manual validation or ticket creation
	* **LINE EXAMPLE:** `MON-SUPER-SITE` exclude all hit where **URL** is like _https://tenant.sharepoint.com/sites/MON-SUPER-SITE/*_
	* **LINE EXAMPLE:** `MON-SUPER-SITE` exclude all hit where **URL** is like _https://on_premise_domain/MON-SUPER-SITE/*_
* ./\_config/path_snaffler_binary.txt: _interactive creation at first launch_
	* **LINE EXAMPLE:** `C:\\SharePointScanner\\_Snaffler\\snaffler.exe`
* ./\_config/specific_regex.txt _manual creation_ - used by "add_regex.py" to search custom regex in download files
	* **LINE EXAMPLE:** `your regex to detect specific username format`
* ./\_config/targeted_sharepoint.txt _interactive creation at first launch_ - 
	* **LINE EXAMPLE:** `https://tenant.sharepoint.com`
	* **LINE EXAMPLE:** `https://on_premise_domain`
	* to avoid operator interaction, just create and complete the file before to start the scan

Result format
-
* source_type: name of the preset that caused detection
* id_file: unique SharePoint ID
* file_status: 
	* `Downloaded` - file downloaded in "./\_downloaded_files_from_sharepoint" 
	* `TooBig` - file note downloaded since it size is greater than "options.txt" `studySharepointUrl - MaxSizeForDownload`
	* `InfoGatheringError` - something went wrong during information gathering for this hit
* data_type: `FromSharePoint:targeted SharePoint`
* url:
* createdDateTime
* lastModifiedDateTime
* size
* name
* mimeType
* createdBy
* createdBy_dpt: see "options.txt" `studySharepointUrl - SpecificProperty`
* downloadUrl: only present if GRAPH API is used
* detection_type:
	* Snaffler information: `Black` / `Red` / `Yellow` / `Green`
	* Regex information: `RegexHit` / `RegexNoHit` / `NoRegexCauseBinary`
* detection_rule: Snaffler detection rule like `KeepCmdCredentials`
* context: Snaffler context detection or regex context detection
* first_scan_detection_date
* last_scan_detection_date
* manual_status: set with `--manual_processing`
* still_present:
	* `0` if no more present
	* `1` if still present
* already_notified: ID of your ticket management platform

Ticket format
-
* type: `USER` - ticket for a single user, `SITE` - ticket for a site where more than "options.txt" `prepareTickets - LimitToNotifySite` different users have a hit, `MISC` - ticket recreate from result with **already_notified** set to a different value than **linked_ticket** of all present tickets
* rev: `0` increment each time that a hit is added to ticket at state `NEW`
* linked_ticket: `2023-XX-XX_POSTED_eebade15...0d89.json` - if new hit for a site already notified with a `SITE` ticket at state `POSTED`
* perimeter: `FromSharePoint:targeted SharePoint`
* status: `NEW` - by default, `POSTED` - sent to your ticket management platform
* id_ticket_ext: ID of your ticket management platform
* hit_resume:
	* average_detection_score
	* nb_hits
	* nb_concerned_users
	* nb_concerned_sites
* hit_infos:
	* concerned_users: list of concerned users
	* concerned_sites: list of concerned sites
* hit: details contained in result file

File tree
-
* \_code: _part of the project_
	* ./: all the functions called by the "main.py" file
	* ./static: contains CSS file for the manual validation WEB application (manual_processing.py)
	* ./templates: contains HTLM files for the manual validation WEB application (manual_processing.py)
* \_config: _part of the project_ please take a look at the "Configuration files" section
* \_data: _automatic creation at first launch_ contains the data created by the scanner. To not keep history, set "options.txt" `archiveResults - VERBOSE_LOG` to "0"
* \_downloaded_files_from_sharepoint: _automatic creation at first launch_ contains all the files downloaded by the scanner
* \_logs: _automatic creation at first launch_ contains all the logs created by the scanner
* \_tickets: _automatic creation at first launch_ contains the result of "--tickets" option
* \_result_history: _automatic creation at first launch_ contains the scan results, modification of this folder content **will** impact the scanner
* \_results: _automatic creation at first launch_ contains the scan results, modification of this folder content will not impact the scanner

Due credits
-

* [l0ss](https://github.com/l0ss) and [Sh3r4](https://github.com/Sh3r4) for Snaffler (https://github.com/SnaffCon/Snaffler)
* [Nicolas Heiniger](https://github.com/nheiniger) for SnaffPoint (https://github.com/nheiniger/SnaffPoint)