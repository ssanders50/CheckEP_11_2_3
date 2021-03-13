import os
from WMCore.Configuration import Configuration
config = Configuration()
from CRABClient.UserUtilities import getUsernameFromSiteDB
cwd = os.getcwd()
print(cwd)

iovs=[1, 326545, 326620, 326887, 327147, 327230, 328000]
niovs = len(iovs)-1
niovs = 1
dataset = '/HIMinimumBias0/HIRun2018A-04Apr2019-v1/AOD'
tag = 'MB0_check'
user = 'ssanders'
json = 'Cert_326381-327560_HI_PromptReco_Collisions18_JSON.txt'
store = 'PbPb2018_04Apr2019'
work = 'crab_projects'
storagesite = 'T2_US_Vanderbilt'
dbfile='HeavyIonRPRcd_PbPb2018_offline.db'

config.section_('General')
config.General.transferOutputs = True
config.General.transferLogs = True
config.section_('JobType')
config.JobType.outputFiles = ['check.root']
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = cwd+'/checkep_cfg.py'
config.JobType.maxJobRuntimeMin = 2500
config.section_('Data')
config.Data.allowNonValidInputDataset = True
config.Data.unitsPerJob = 160
config.Data.publication = False
config.Data.splitting = 'LumiBased'
config.section_('User')
config.section_('Site')
config.Site.storageSite = storagesite
config.JobType.allowUndistributedCMSSW = True

if __name__ == '__main__':

    from CRABAPI.RawCommand import crabCommand
    from httplib import HTTPException

    # We want to put all the CRAB project directories from the tasks we submit here into one common directory.
    # That's why we need to set this parameter (here or above in the configuration file, it does not matter, we will not overwrite it).
    config.General.workArea = 'crab_projects'

    def submit(config):
        try:
            crabCommand('submit', config = config)
        except HTTPException, hte:
            print hte.headers

    #############################################################################################
    ## From now on that's what users should modify: this is the a-la-CRAB2 configuration part. ##
    #############################################################################################

for i in range(0, niovs):
    print(' =============== ')
    print(iovs[i])
    dataset = dataset
    print(dataset)
    runrange = str(iovs[i])+'-'+str(iovs[i+1]-1)
    runranges = str(iovs[i])+'_'+str(iovs[i+1]-1)

    print(runrange)

    remotestore = store+'_'+tag+'_'+runranges
    dirbase = '/store/user/'+user+'/'+remotestore
    config.General.requestName = remotestore
    config.Data.outLFNDirBase = dirbase
    config.Data.lumiMask = json
    config.Data.runRange = runrange
    config.JobType.inputFiles = [ json, dbfile ]
    config.JobType.pyCfgParams = ['noprint','lumifile='+json,'aodType=AOD','dbfile='+dbfile]
    config.Data.inputDataset = dataset

    submit(config)

