import json
import os
import subprocess

class hpacuclimon(object):
    def __init__(self, workingDir: str):
        os.makedirs(workingDir, exist_ok=True)
        self.workingDir = workingDir
        self.fileNameState = workingDir + '/' + self.__class__.__name__ + '.state'
        if os.path.exists(self.fileNameState):
            with open(self.fileNameState, 'r') as file_handle:
                self.state = json.load(file_handle)
                if 'failed' not in self.state:
                    self.state['failed'] = False
        else:
            self.state = {}
            self.state['failed'] = False
        self.__writeState = False
        self.report = {}

    def __del__(self):
        if self.__writeState != False:
            try:
                with open(self.fileNameState, 'w') as file_handle:
                    json.dump(self.state, file_handle, indent=4)
            except:
                """Its okay, the state is not saved, but next time will be assumed not failed"""

    def generateReport(self, saveToDisk=False, debugReportFile=''):
        if debugReportFile == '':
            self.report['output'] = {}
            self.report['output']['config'] = subprocess.check_output(['hpacucli','ctrl', 'all', 'show', 'config']).decode().split('\n')
            self.report['output']['detail'] = subprocess.check_output(['hpacucli','ctrl', 'all', 'show', 'detail']).decode().split('\n')
            
            """Decode the details, then go get the data"""
            self.report['details'] = {}
            details = {}
            for line in self.report['output']['detail']:
                if line.strip() != '':
                    if line[0] != ' ':
                        if details != {}:
                            if 'slot' in details:
                                self.report['details'][details['slot']] = details
                            details = {}
                        details['header'] = line.strip()
                    else:
                        line_split = line.split(':')
                        try:
                            details[line_split[0].lower().strip()] = line_split[1].lower().strip()
                        except:
                            """Nothing to do, something I dont exactly expect"""
            if details != {} and 'slot' in details:
                self.report['details'][details['slot']] = details

            """Go get all the drive status"""
            self.report['pds'] = {}
            self.report['output']['pd'] = {}
            for slot in self.report['details']:
                self.report['output']['pd'][slot] = subprocess.check_output(['hpacucli', 'ctrl', 'slot={0}'.format(slot), 'pd', 'all', 'show', 'detail']).decode().split('\n')

                pds = {}
                array_name = 'bad_array_name'
                drive_name = 'bad_drive_name'
                for line in self.report['output']['pd'][slot]:
                    if line.strip() != '':
                        line = line.replace('\t','   ')
                        line_split = line.split(':')
                        if (len(line) > 9 and line[0:9]) == '         ':
                            """Drive Info"""
                            pds[array_name][drive_name][line_split[0].lower().strip()] = line_split[1].lower().strip()

                        elif len(line) > 6 and line[0:6] == '      ':
                            """Drive Name"""
                            drive_name = line.strip()
                            pds[array_name][drive_name] = {}

                        elif len(line) > 3 and line[0:3] == '   ':
                            """Array Name"""
                            array_name = line.strip()
                            pds[array_name] = {}
                        
                if pds != {}:
                    self.report['pds'][slot] = pds

        else:
            with open(debugReportFile, 'r') as file_handle:
                self.report = json.load(file_handle)

        if saveToDisk != False:
            file_name = self.workingDir + '/' + self.__class__.__name__ + '.report'
            with open(file_name, 'w') as file_handle:
                json.dump(self.report, file_handle, indent=4)
        
        return self.report
    
    def getMonitorStatus(self):
        if self.report == {}:
            self.generateReport()
        
        failed = False

        for slot in self.report['details']:
            if 'battery/capacitor status' in self.report['details'][slot] and self.report['details'][slot]['battery/capacitor status'] != 'ok':
                failed = True

            if 'controller status' in self.report['details'][slot] and self.report['details'][slot]['controller status'] != 'ok':
                failed = True

            if 'cache status' in self.report['details'][slot] and self.report['details'][slot]['cache status'] != 'ok':
                failed = True
        
        for slot in self.report['pds']:
            for array in self.report['pds'][slot]:
                for disk in self.report['pds'][slot][array]:
                    if 'status' in self.report['pds'][slot][array][disk] and self.report['pds'][slot][array][disk]['status'] != 'ok':
                        failed = True

        return_data = {}
        return_data['old'] = self.state['failed']
        return_data['cur'] = failed

        if self.state['failed'] != failed:
            self.state['failed'] = failed
            self.__writeState = True

        return return_data
    
    def serializeReport(self):
        if self.report == {}:
            self.generateReport()
        return json.dumps(self.report, indent=4)
