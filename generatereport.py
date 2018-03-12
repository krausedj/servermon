import argparse
import emailmon
import hpacuclimon

parser = argparse.ArgumentParser()
#parser.add_argument('--user', required=True, help='gmail user name')
#parser.add_argument('--password', required=True, help='gmail password')
#parser.add_argument('--emailto', required=True, help='person to send email to')
parser.add_argument('--workingdir', required=True, help='working directory for storing reports and current state')
args = parser.parse_args()

hpmon = hpacuclimon.hpacuclimon(workingDir=args.workingdir)
hpmon.generateReport(saveToDisk=True)