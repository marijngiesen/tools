#!/usr/bin/python

import os, sys, shutil
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from email.mime.text import MIMEText

TRACADMIN_BIN = "/usr/bin/trac-admin "
SENDMAIL_BIN  = "/usr/sbin/sendmail"
SENDMAIL_OPTS = "-t"
STATUSMAIL_TO = "your@email.com"

def create_backupdir(backupRoot, project = None):
	if project is not None:
		backupRoot = os.path.join(backupRoot, project)

	backupDirWeekDay = os.path.join(backupRoot, str(datetime.today().weekday()))
	if os.path.isdir(backupDirWeekDay):
		shutil.rmtree(backupDirWeekDay)

	try:
		os.makedirs(backupRoot)
	except Exception, e:
		pass

	return backupDirWeekDay


def do_backup(tracDir, backupDir):
	cmd = TRACADMIN_BIN + tracDir + " hotcopy " + backupDir
	process = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
	output, err = process.communicate()
	retcode = process.poll()

	if retcode != 0:
		msg = MIMEText("TRAC backup failed:\n\nretcode = " + str(retcode) + "\ncmd = " + str(cmd) + "\noutput = " + str(output) + "\n")
		msg["From"]    = "trac-backup@rdprojects.umcn.nl"
		msg["To"]      = STATUSMAIL_TO
		msg["Subject"] = "TRAC backup failed"

		pipe = Popen([SENDMAIL_BIN, SENDMAIL_OPTS], stdin=PIPE)
		pipe.communicate(msg.as_string())


if __name__ == "__main__":

	if len(sys.argv) != 3:
	    print "Usage: " + os.path.basename(__file__) + " <trac-directory> <backup-directory>"
	    sys.exit(1)

	tracRoot   = sys.argv[1]
	backupRoot = sys.argv[2]
	if not os.path.isdir(tracRoot):
	    print "Error: TRAC directory " + tracRoot + " does not exist"
	    sys.exit(1)

	files = os.listdir(tracRoot)
	if "VERSION" in files:
		# This is a single project instance
		do_backup(tracRoot, create_backupdir(backupRoot))
		sys.exit(0)
		
	projects = [name for name in files if os.path.isdir(os.path.join(tracRoot, name))]
	for project in projects:
		tracDir = os.path.join(tracRoot, project)
		if not "VERSION" in os.listdir(tracDir):
			# This is not a TRAC project, skip it.
			continue

		do_backup(tracDir, create_backupdir(backupRoot, project))


