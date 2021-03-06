import os
import subprocess
import re
import sys
import csv

if len(sys.argv) < 3:
	print("./repossesd <github_user> <repo>")
	sys.exit(-1)
repo_user = sys.argv[1]
repo = sys.argv[2]


fnull = open(os.devnull, 'w')


subprocess.check_output(['rm','-rf','%s' % repo])

a = subprocess.check_output(['git', 'clone', "https://github.com/%s/%s" % (repo_user,repo)],stderr=fnull)


bad_file_regexs = {}
with open('badfilename_regex.csv', 'rb') as csvfile:
	badfilenamefile = csv.reader(csvfile)
	for row in badfilenamefile:
		bad_file_regexs[row[0]] = row[1]
del(bad_file_regexs["REGEX"])

bad_string_regexs = {}
with open('badstrings_regex.csv', 'rb') as csvfile:
	badstringfile = csv.reader(csvfile)
	for row in badstringfile:
		 bad_string_regexs[row[0]] = row[1]
del(bad_string_regexs["REGEX"])


os.chdir(repo)
a = subprocess.check_output(['git','log'],stderr=fnull)

commits = []
b = a.split("\n")
for c in b:
	if c[:6] == "commit":
		commits.append(c.split(" ")[1])

matchfiles = {}

print "scanning repository histories for repo %s" % "https://github.com/%s/%s" % (repo_user,repo)
for c in commits:
	print "\tscanning repo commit %s" % c
	filelist = []
	a = subprocess.check_output(['git','checkout','%s' % c],stderr=fnull)
	for root, directories, filenames in os.walk("."):
		for item in filenames:
			fileNamePath = os.path.join(root,item)
			#print fileNamePath
			
			for rex,val in bad_file_regexs.items():
				if re.match(rex, item):
					matchfiles[fileNamePath] = {"regex":rex,"val":val,"commit":c,"file":item, "offset":[],"type":"filename"}
				else:
					if re.match(rex, fileNamePath):
						matchfiles[fileNamePath] = {"regex":rex,"val":val,"commit":c,"file":item, "offset":[],"type":"filename"}
		
			for rex,val in bad_string_regexs.items():
				p = re.compile(rex)
				try:
					f = open(fileNamePath)
					tfile = f.read()
					f.close()
				except:
					tfile = "" #eh.. it'll be fast
				
				for m in p.finditer(tfile):
					t = {"regex":rex,"val":val,"commit":c,"file":item,"offset":[], "type":"contents"}
					t["offset"].append(m.start())
					matchfiles[fileNamePath] = t
os.chdir("..")

print("************************************************************")
for f,dat in matchfiles.items():
	print "Match in \"%s\" in commit %s with regex \"%s\"" % (f,dat["commit"],dat["regex"])
	for o in dat["offset"]:
		print "\t@%d bytes offset" % o


