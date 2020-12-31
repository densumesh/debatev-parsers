import json
import os

import requests
import urllib3
from alive_progress import alive_bar

urllib3.disable_warnings()
import hashlib
import re

import docx2txt
import textile
from elasticsearch import Elasticsearch
import sys

def PFcardparser (filepath, filelink, year):
  allcards = ''

  allHtml = {} #dictionary with all cards
  textfromdoc = docx2txt.process(filepath) # docx to text
  htmlfromdoc = textile.textile(textfromdoc) #this is not a file, but instead a string
  #print(htmlfromdoc)
  j=1
  matches = re.findall(r'<p>.+?</p>', htmlfromdoc) #generates list of all html code between <p> tags

  for i in matches:
    
    if 'http' in i:
      x = matches.index(i)
      if len(i) <= 800 and len(matches[x+1]) > 280:
        if i[:7] == '<p>http':
          if len(matches[x-1]) < 400:

            titleandlink = matches[x-1] + i
            maintext = matches[x+1]
            allcards += titleandlink
            allcards += maintext
            allHtml["card " + str(j)] = [{"tag+cite": titleandlink, "cardHtml": maintext, "dtype": "pf", "filepath": filelink, "year":year}]
            j += 1
        else:
          titleandlink = i   #link and maybe title as a string(ex. Lawrence Goodman, 11-6-2020, “COVID-19 ravages Iran,” BrandeisNOW,
          maintext = matches[x+1]
          allcards += titleandlink
          allcards += maintext
          allHtml["card " + str(j)] = [{"tag+cite": titleandlink, "cardHtml": maintext, "dtype": "pf", "filepath": filelink, "year":year}]
          j += 1
        
  return allHtml



es = Elasticsearch(hosts = [{'host': 'localhost', 'port':9200}], verify_certs = False, use_ssl = True)

def uploadcase(z, dtype):
    for i in range(len(z)):
        tag = z['card '+ str(i + 1)][0]['tag+cite']
        cardHtml = z['card '+ str(i + 1)][0]['cardHtml']
        
        filepath = z['card '+ str(i + 1)][0]['filepath']
        year = z['card '+ str(i + 1)][0]['year']
        x = hashlib.sha224(bytes(tag, 'utf-8')).hexdigest()
        es.index(index=dtype, doc_type='cards', id=x, body={
        "tag+cite": tag,
        "cardHtml": cardHtml,
        "filepath": filepath,
        "year": year
        })


with alive_bar(1623) as bar:
    for i in range(7, 10):
        with open(f'/Users/family/Downloads/uploadpf/wikiUrls/wikijson/201{i}pfwiki.json', 'r') as fp:
            data = json.load(fp)
        for carddata in data['rows']:
            
            try:
                if '.docx' in carddata['filename']:
                    response = requests.get(f'https://hspf1{i}.debatecoaches.org' + carddata['fileurl'])
                    with open('/Users/family/Downloads/uploadpf/Python scripts/pf_files' + carddata['filename'], 'wb') as f:
                        f.write(response.content)
                        z = PFcardparser('/Users/family/Downloads/uploadpf/Python scripts/pf_files' + carddata['filename'], f'https://hspf1{i}.debatecoaches.org' + carddata['fileurl'], f"201{i}")

                        uploadcase(z, "pf")
                        os.remove('/Users/family/Downloads/uploadpf/Python scripts/pf_files'+carddata['filename'])
                        bar()
            except Exception as e:
                print(e)
                pass


with open(f'/Users/family/Downloads/uploadpf/wikiUrls/wikijson/2020pfwiki.json', 'r') as fp:
        data = json.load(fp)
        for carddata in data['rows']:
            try:
                if '.docx' in carddata['filename']:
                    response = requests.get(f'https://hspf.debatecoaches.org' + carddata['fileurl'])
                    with open('/Users/family/Downloads/uploadpf/Python scripts/pf_files' + carddata['filename'], 'wb') as f:
                        f.write(response.content)
                        z = PFcardparser('/Users/family/Downloads/uploadpf/Python scripts/pf_files' + carddata['filename'], f'https://hspf.debatecoaches.org' + carddata['fileurl'], f"2020")
                        uploadcase(z, "pf")
                        os.remove('/Users/family/Downloads/uploadpf/Python scripts/pf_files'+carddata['filename'])
                        bar()
            except Exception as e:
                print(e)
                pass
