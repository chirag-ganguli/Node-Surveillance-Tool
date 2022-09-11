import csv
import sys
import os
import shutil
import argparse
import json
import pandas as pd
import urllib.request
import colorama
from colorama import Fore
#from openpyxl.workbook import Workbook

print(Fore.CYAN + """
   )                  (                                                   
 ( /(       (          )\ )                      (  (                      
 )\())      )\ )  (   (()/(  (  (    )     (  (  )\ )\   )             (   
((_)\  (   (()/( ))\   /(_))))\ )(  /((   ))\ )\((_|(_| /(  (     (   ))\  
 _((_) )\   ((_))((_) (_)) /((_|()\(_))\ /((_|(_)_  _ )(_)) )\ )  )\ /((_) 
| \| |((_)  _| (_))   / __(_))( ((_))((_|_))  (_) || ((_)_ _(_/( ((_|_))
| .` / _ \/ _` / -_)  \__ \ || | '_\ V // -_) | | || / _` | ' \)) _|/ -_)  
|_|\_\___/\__,_\___|  |___/\_,_|_|  \_/ \___| |_|_||_\__,_|_||_|\__|\___|
""" + Fore.RESET)

# Import Argument Parser
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, required=True)
parser.add_argument('-u', '--update', action='store_true')
parser.add_argument('-v', '--version', type=str)
args = parser.parse_args()

# Go through the user inputted arguments
if(args.input):
    with open(args.input) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        aa = pd.read_csv(args.input)

        # Change the below paths in accordance to the OS on which the script is being run
        src = os.path.join("/Users/chiragganguli/Documents/Projects/Dyte_CLI/dyte-vit-2022-chirag-ganguli/", args.input)
        dst = "/Users/chiragganguli/Documents/Projects/Dyte_CLI/dyte-vit-2022-chirag-ganguli/{0}copy.csv".format(args.input.split('.')[0])
        path = shutil.copyfile(src, dst)

        # Replaces github.com with raw.githubusercontent.com
        text = open("nodemonitordata.csv", "r")
        text = ''.join([i for i in text])
        text = text.replace("github", "raw.githubusercontent")
        x = open("nodemonitordata.csv","w")
        x.writelines(text)
        x.close()

        line_count = 0
        versioninfo = []
        versionsatisfied = []
        i = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                print(f'\tReading {row[1]}')
                url = f'{row[1]}/main/package.json'
                df = pd.read_json(url)
                df.to_excel('tmpURLExcel.xlsx')
                df.to_csv('tempURL.csv') #header=False
                with open('tempURL.csv') as search_file:
                    csv_reader2 = csv.reader(search_file, delimiter=',')
                    line_count2 = 0
                    for row in csv_reader2:
                        if(row[0] == args.version.split('@')[0]):
                            if(str(df.loc[args.version.split('@')[0], 'dependencies']) != ""):
                                versioninfo.append(str(df.loc[args.version.split('@')[0], 'dependencies']))
                            else:
                                versioninfo.append(str(df.loc[args.version.split('@')[0], 'devDependencies']))
                if(versioninfo[i].split('.')[0] >= args.version.split('@')[1].split('.')[0] and versioninfo[i].split('.')[1] >= args.version.split('@')[1].split('.')[1] and versioninfo[i].split('.')[2] >= args.version.split('@')[1].split('.')[2]):
                    versionsatisfied.append("true")
                else:
                    versionsatisfied.append("false")
                i += 1 
                line_count += 1
    aa["version"] = versioninfo
    aa["version_satisfied"] = versionsatisfied
    aa = aa.stack().str.replace('^', '').unstack()
    print("\n")
    print(aa)
    print("\n")
    aa.to_csv(args.input, index = False)

if(args.update):
    openpath = args.input.split('.')[0]
    openpath = openpath + 'copy.csv'
    aaa = pd.read_csv(args.input)
    with open(openpath) as newfile:
        csv_reader = csv.reader(newfile, delimiter=',')
        updatepr = []
        line_count = 0
        counter = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                print(f'\tReading {row[1]}')
                if(versionsatisfied[counter] == "false"):
                    url = f'{row[1]}'
                    urlcut = url.split('/')[4]
                    # FORK the remote repository
                    # Use Y in the CLI to clone the repository in the local directory
                    os.system("gh repo fork {0}".format(url))
                    inputsp = url.split('/')[2]
                    os.chdir(urlcut)
                    os.system("ls")
                    os.system("npm install {0}".format(args.version))
                    os.system("git add .")
                    os.system("git commit -m 'Updated Packages'")
                    os.system("git push")
                    os.system("gh pr create --title 'Updated Package to {0}' --body 'Pull request made' > ../PRurl.txt".format(args.version))
                    with open('../PRurl.txt', 'r') as f:
                        for line in f:
                            updatepr.append(line.strip())
                else:
                    updatepr.append(str(""))
                counter += 1
    os.chdir("../")
    aaa["update_pr"] = updatepr
    print("\n")
    print(aaa)
    print("\n")
    aaa.to_csv(args.input, index = False)
    aaa.to_excel("finaloutput.xlsx", index = False)

text = open("nodemonitordata.csv", "r")
text = ''.join([i for i in text])   
text = text.replace("raw.githubusercontent", "github") 
x = open("finaloutput.csv","w")
x.writelines(text)
x.close()