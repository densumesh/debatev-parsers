import json
import requests
from alive_progress import alive_bar
from wordToHtml import converttoHTML
from uploadcase import uploadcase
import os 
import urllib3
urllib3.disable_warnings()
with alive_bar(22031) as bar:
    for i in range(4, 10):
        if not i == 7:
            with open(f'wikiUrls/wikijson/201{i}collegepolicy.json', 'r') as fp:
                data = json.load(fp)
            for carddata in data['rows']:
                try:
                    if '.docx' in carddata['filename']:
                        response = requests.get(f'https://opencaselist1{i}.paperlessdebate.com' + carddata['fileurl'])
                        with open('college_policy_files/' + carddata['filename'], 'wb') as f:
                            f.write(response.content)
                            z = converttoHTML('college_policy_files/' + carddata['filename'], f'https://opencaselist1{i}.paperlessdebate.com' + carddata['fileurl'], 'College Policy')
                            uploadcase(z)
                            os.remove('college_policy_files/'+carddata['filename'])
                            bar()
                except Exception as e:
                    print(e)
                    pass
with alive_bar(25101) as bar:
    for i in range(4, 10):
        with open(f'wikiUrls/wikijson/201{i}ldwiki.json', 'r') as fp:
            data = json.load(fp)
        for carddata in data['rows']:
            if '.docx' in carddata['filename']:
                response = requests.get(f'https://hsld1{i}.debatecoaches.org' + carddata['fileurl'])
                with open('ld_files/' + carddata['filename'], 'wb') as f:
                    f.write(response.content)
                    converttoHTML('ld_files/' + carddata['filename'], f'https://hsld1{i}.debatecoaches.org' + carddata['fileurl'], "LD")
                    bar()
with alive_bar(22397) as bar:
    for i in range(4, 10):
        with open(f'wikiUrls/wikijson/201{i}policywiki.json', 'r') as fp:
            data = json.load(fp)
        for carddata in data['rows']:
            if '.docx' in carddata['filename']:
                response = requests.get(f'https://hspolicy1{i}.debatecoaches.org' + carddata['fileurl'])
                with open('hs_policy_files/' + carddata['filename'], 'wb') as f:
                    f.write(response.content)
                    converttoHTML('hs_policy_files/' + carddata['filename'], f'https://hspolicy1{i}.debatecoaches.org' + carddata['fileurl'], "High School Policy")
                    bar()

with alive_bar(829) as bar:
    for i in range(7, 10):
        with open(f'wikiUrls/wikijson/201{i}pfwiki.json', 'r') as fp:
            data = json.load(fp)
        for carddata in data['rows']:
            if '.docx' in carddata['filename']:
                response = requests.get(f'https://hspf1{i}.debatecoaches.org' + carddata['fileurl'])
                with open('pf_files/' + carddata['filename'], 'wb') as f:
                    f.write(response.content)
                    converttoHTML('pf_files/' + carddata['filename'], f'https://hspf1{i}.debatecoaches.org' + carddata['fileurl'], "PF")
                    bar()