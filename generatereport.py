import argparse
import emailmon
import hpacuclimon

parser = argparse.ArgumentParser()
parser.add_argument('--user', required=True, help='gmail user name')
parser.add_argument('--password', required=True, help='gmail password')
parser.add_argument('--emailto', required=True, help='person to send email to')
parser.add_argument('--workingdir', required=True, help='working directory for storing reports and current state')
parser.add_argument('--idname', required=True, help='name of server or unique id')
parser.add_argument('--emailforce', default=False, action='store_true', help='if you want the report emailed regardless of a failure status change')
args = parser.parse_args()

if args.emailforce != False:
    email_report = True
else:
    email_report = False

body = ''

fail_count = 0
title_fail = ''

hpmon = hpacuclimon.hpacuclimon(workingDir=args.workingdir)
hpmon.generateReport(saveToDisk=True)

failure = hpmon.getMonitorStatus()
if failure['cur'] != failure['old']:
    email_report = True
    if failure['cur'] != False:
        fail_count += 1
        title_fail = title_fail + ' RAID'

if failure['cur'] != False or args.emailforce != False:
    body = body + '\n\n' + hpmon.serializeReport()

if email_report != False:
    if fail_count > 0:
        title = args.idname + ' FAIL' + title_fail
    else:
        title = args.idname + ' PASS'
    
    emailmon.sendemail(user=args.user, password=args.password, email_to=args.email_to, subject=title, body=body )
