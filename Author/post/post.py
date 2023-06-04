#!/usr/bin/env python3

# Author: Mathew Potts
# Date: 2022/03/14
# Purpose: Post TA author files to tadserv
############################################################################################################
## IMPORT LIBS
import re
import os
import sys
import datetime as dt
try:
    import requests
    from bs4 import BeautifulSoup as bs
except ModuleNotFoundError:
    sys.exit("ERROR: Datascrapper requires python3-bs4 & python3-requests")
######################################################################################################

## CLASSES

## GET_ACCESSLIST
class POST_AUTHORLIST:
    def __init__(self,login_usr,login_pw,usr,pw):
        # Start Requests Session
        self.session = requests.Session()
        self.session.auth = (login_usr,login_pw)
        
        # URLS
        self.edit_url  = 'http://tadserv.physics.utah.edu/TA-ICRC-09/index.php?title=TA_author_list_and_acknowledgements&action=edit'
        login_url = 'http://tadserv.physics.utah.edu/TA-ICRC-09/index.php?title=Special:UserLogin&returnto=TA+author+list+and+acknowledgements' 

        # Log-in to tadserv
        response = self.session.get(login_url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            sys.exit("ERROR: {}".format(e))
        self.login_soup = bs(response.text,'html.parser')
        
        # Form info that will be passed to wiki to log-in
        form_data = {
            'wpName'       : usr,
            'wpPassword'   : pw,
            'wpRemember'   : '1',
            'authAction'   : 'login',
            'wpLoginToken' : ''
        }
        
        # Grabbing Login Token from log-in requests
        form_data['wpLoginToken'] = self.login_soup.find('input',attrs={'name':'wpLoginToken'})['value']   

        # Log-in to Tadserv
        self.response = self.session.post(login_url, data=form_data,)

        # GET request after log-in
        edit_response = self.session.get(self.edit_url)
        self.edit_soup = bs(edit_response.text,'html.parser')
        
    def construct_content(self, new_dates, authors, institutions, countries, authbycount, top5):
        # This function parses the author list files to get the last date of the access list and
        # acknoledgements, then it constructs a string that will posted on the wiki page. The
        # only issue with pasting html code in the wiki are <a> tags. I need a fundtion that
        # converst html <a> tags to wiki text code.
        content = self.edit_soup.find('textarea').get_text()
        lines = content.splitlines()
        
        # Replace author and acknowledgement dates on first line
        old_dates =  re.findall(r"\d\d\d\d\d\d\d\d",lines[0])
        for i in range(2):
            content = content.replace(old_dates[i],new_dates[i],1)

        # Change old dates of LaTex <a> tags to new dates
        content = content.replace(old_dates[0].replace('/',''),new_dates[0].replace('/',''),14)
        content = content.replace(old_dates[1].replace('/',''),new_dates[1].replace('/',''),2)
        
        # Replace number of authors, institutions, countries
        authors_old      = re.findall(r"\d+ authors", content)[0]
        institutions_old = re.findall(r"\d+ institutions", content)[0]
        countries_old    = re.findall(r"\d+ countries", content)[0]
        old_misc = [authors_old,institutions_old,countries_old]
        new_misc = [authors+' authors',institutions+' institutions',countries+' countries']
        for i in range(3):
            content = content.replace(old_misc[i],new_misc[i])

        # Replace Tables
        old_authbycount = re.findall(r"(?<=\n)\|\s.*\s\|\|\s\d+\s\|\|\s\d+(?=\n)",content)
        old_top5 = re.findall(r"(?<=\n)\|\s(?:\w+|\w+\s\w+|\w+\s\w+\s\w+)\s\|\|\s\d+(?=\n)",content)
        old_tabs = [old_authbycount, old_top5]
        for i in range(len(old_tabs)):
            tab = authbycount if i == 0 else top5
            for j in range(len(tab)):
                new_ent = '| {0} || {1} || {2}'.format(*authbycount[j]) if i == 0 else '| {0} || {1}'.format(*top5[j])
                content = content.replace(old_tabs[i][j], new_ent,1)
         
        # Added the old author list files to Older versions
        search = "'''Older versions:'''"
        start_point = content.find(search) + len(search)
        add_string = '\n*TA author list (as of {0}) and acknowledgements (as of {1}): [[Media:TA-author-{0}.tex|TA-author-{0}.tex]] [[Media:TA-author-{0}-authblk.tex|TA-author-{0}-authblk.tex]] [[Media:TA-author-{0}-aastex.tex|TA-author-{0}-aastex.tex]] [[Media:TA-author-{0}-arxivSubmit.txt|TA-author-{0}-arxivSubmit.txt]] [[Media:TAacknowledgements-{1}.tex|TAacknowledgements-{1}.tex]] [[Media:TA-author-{0}.pdf|TA-author-{0}.pdf]] [[Media:TA-author-{0}.png|TA-author-{0}.png]]\n'.format(old_dates[0].replace('/',''),old_dates[1].replace('/',''))

        # Check to see if the files are already in the Older versions list
        if add_string in content: # if it is don't add the string
            print("These files are already in the Older version. Not adding these files to Older version list.")
        else: # if it isn't in the list add it to the content string
            content = content[:start_point] + add_string + content[start_point:]
        
        return content
              
    def post_authorlist_content(self,string):
        # Form info that will be passed to wiki
        form_data = {
            'wpUnicodeCheck' : '',
            'wpAntispam' : '',
            'wpSection':'',
            'wpStarttime': '',
            'wpEdittime': '',
            'editRevId' : '',
            'wpScrolltop': '',
            'oldid' : '',
            'wpAutoSummary': '',
            'parentRevId': '',
            'wpTextbox1': string,
            'wpSummary':'',
            'wpSave': 'Save changes',
            'wpEditToken':  '',
            'wpUltimateParam' : ''
        }

        # Grabbing form info from GET request
        form_data['wpUnicodeCheck']  = self.edit_soup.find('input',attrs={'name':'wpUnicodeCheck'})['value']
        form_data['wpAntispam']      = self.edit_soup.find('input',attrs={'name':'wpAntispam'})['value']
        form_data['wpStarttime']     = self.edit_soup.find('input',attrs={'name':'wpStarttime'})['value']
        form_data['wpEdittime']      = self.edit_soup.find('input',attrs={'name':'wpEdittime'})['value']
        form_data['editRevId']       = self.edit_soup.find('input',attrs={'name':'editRevId'})['value']
        form_data['parentRevId']     = self.edit_soup.find('input',attrs={'name':'parentRevId'})['value']
        form_data['wpAutoSummary']   = self.edit_soup.find('input',attrs={'name':'wpAutoSummary'})['value']
        form_data['wpoldid']         = self.edit_soup.find('input',attrs={'name':'oldid'})['value']
        form_data['wpSummary']       = self.edit_soup.find('input',attrs={'name':'wpSummary'})['value']
        form_data['wpEditToken']     = self.edit_soup.find('input',attrs={'name':'wpEditToken'})['value']
        form_data['wpUltimateParam'] = self.edit_soup.find('input',attrs={'name':'wpUltimateParam'})['value']

        # POST request
        self.session.post(self.edit_url,data=form_data,)
        
    def post_authorlist_files(self,files):
        # Construct Upload Post data
        form_data = {
            'wpEditToken':  '',
            'wpDestFile' : '',
            'wpWatchthis' : '',
            'wpIgnoreWarning' : '',
            'wpUploadDescription' : '',
            'wpUpload' : 'Upload file',  
        }
        for f in files:
            # Construct url for file and file object
            url = 'http://tadserv.physics.utah.edu/TA-ICRC-09/index.php?title=Special:Upload&wpDestFile={0}'.format(f.split('/')[-1]) # url
            filename = {'wpUploadFile' : (f.split('/')[-1],open(f,'rb'),'multipart/form-data')} # filename object for post request

            # GET requests to fill form_data
            response = self.session.get(url)
            soup = bs(response.text,'html.parser')
            form_data['wpEditToken'] = soup.find('input',attrs={'name':'wpEditToken'})['value']
            form_data['wpDestFile'] = soup.find('input',attrs={'name':'wpDestFile'})['value']
            form_data['wpWatchthis'] = soup.find('input',attrs={'name':'wpWatchthis'})['value']
            form_data['wpIgnoreWarning'] = soup.find('input',attrs={'name':'wpIgnoreWarning'})['value']
            
            if form_data['wpDestFile'] == f.split('/')[-1]:
                # POST upload filename object
                print(f"Uploading {f}...")
                r= self.session.post(url, data=form_data, files=filename)
            else:
                # Print Error
                print('ERROR: wpUploadFile does not equal wpDestFile - [wpUploadFile = {0}, wpDestFile = {1}]')
