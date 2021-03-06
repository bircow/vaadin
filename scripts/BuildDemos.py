#coding=UTF-8

# See BuildArchetypes for details on environment
# BuildDemos needs git in PATH and depends on gitpython library
# gitpython can be installed with python installer script "pip":
# pip install gitpython	
#
# Deployment dependency: requests
# pip install requests
# Deploy depends on .deployUrl and .deployCredentials files in home folder

import sys, os
from os.path import join, isfile
from fnmatch import fnmatch
from xml.etree.ElementTree import ElementTree

# Validated demos. name -> git url
demos = {
	"dashboard" : "https://github.com/vaadin/dashboard-demo.git",
	"addressbook" : "https://github.com/vaadin/addressbook.git",
	"framework8-demo" : "https://github.com/vaadin/framework8-demo",
	"sampler" : "demos/sampler"
#	"my-demo" : ("my_demo_url_or_path", "my-demo-dev-branch")
}

def checkout(folder, url, repoBranch = "master"):
	Repo.clone_from(url, join(resultPath, folder), branch = repoBranch)

if __name__ == "__main__":
	# Do imports.	
	try:
		from git import Repo
	except:
		print("BuildDemos depends on gitpython. Install it with `pip install gitpython`")
		sys.exit(1)
	from BuildHelpers import updateRepositories, mavenValidate, copyWarFiles, getLogFile, removeDir, getArgs, mavenInstall, resultPath, readPomFile, parser
	from DeployHelpers import deployWar
	# Add command line agrument for ignoring failing demos
	parser.add_argument("--ignore", type=str, help="Ignored demos", default="")
	args = getArgs()
	demosFailed = False
	ignoredDemos = args.ignore.split(",")
	
	wars = []

	for demo in demos:
		print("Validating demo %s" % (demo))
		try:
			repo = demos[demo]
			if (isinstance(repo, tuple)):
				checkout(demo, repo[0], repo[1])
			else:
				checkout(demo, repo)
			if hasattr(args, "fwRepo") and args.fwRepo is not None:
				updateRepositories(join(resultPath, demo), args.fwRepo)
			if hasattr(args, "pluginRepo") and args.pluginRepo is not None:
				updateRepositories(join(resultPath, demo), args.pluginRepo, postfix="plugin")
			mavenValidate(demo, logFile=getLogFile(demo))
			wars.extend(copyWarFiles(demo))
			print("%s demo validation succeeded!" % (demo))
		except Exception as e:
			print("%s demo validation failed: %s" % (demo, e))
			if demo not in ignoredDemos:
				demosFailed = True
		except EnvironmentError as e:
			print("%s demo validation failed: %s" % (demo, e))
			if demo not in ignoredDemos:
				demosFailed = True
		try:
			removeDir(demo)
		except:
			pass
		print("")

	for war in wars:
		try:
			deployWar(war)
		except Exception as e:
			print("War %s failed to deploy: %s" % (war, e))
			demosFailed = True

	if demosFailed:
		sys.exit(1)
