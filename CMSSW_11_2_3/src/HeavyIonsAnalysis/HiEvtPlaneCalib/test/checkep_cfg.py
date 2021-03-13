import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
import os
import sys
ivars = VarParsing.VarParsing('standard')

ivars.register ('lumifile',
                'Cert_326381-327564_HI_PromptReco_Collisions18_JSON.txt',
                mult=ivars.multiplicity.singleton,
                mytype=ivars.varType.string,
                info="lumi file")


ivars.register ('dbfile',
                'HeavyIonRPRcd_offline.db',
                mult=ivars.multiplicity.singleton,
                mytype=ivars.varType.string,
                info="dbfile file")

ivars.register ('checkfile',
                'check.root',
                mult=ivars.multiplicity.singleton,
                mytype=ivars.varType.string,
                info="check output file")

ivars.register ('aodType',
                'AOD',
                mult=ivars.multiplicity.singleton,
                mytype=ivars.varType.string,
                info="AOD/TestAOD/MiniAOD")

ivars.register ('repFile',
                'infile.root',
                mult=ivars.multiplicity.singleton,
                mytype=ivars.varType.string,
                info="single file replay")

ivars.parseArguments()

process = cms.Process("check")
process.load('Configuration.StandardSequences.Services_cff')
process.load("CondCore.CondDB.CondDB_cfi")
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
if ivars.aodType == 'AOD':
	process.load("RecoVertex.PrimaryVertexProducer.OfflinePrimaryVerticesRecovery_cfi")
	process.load('HeavyIonsAnalysis.EventAnalysis.clusterCompatibilityFilter_cfi')
	process.load("HeavyIonsAnalysis.Configuration.hfCoincFilter_cff")
	process.load("HeavyIonsAnalysis.Configuration.analysisFilters_cff")
	process.load('HeavyIonsAnalysis.EventAnalysis.skimanalysis_cfi')
	process.load("HeavyIonsAnalysis.Configuration.collisionEventSelection_cff")

process.load("HeavyIonsAnalysis.HiEvtPlaneCalib.checkflattening_cfi")
process.load("RecoHI.HiEvtPlaneAlgos.HiEvtPlane_cfi")
process.load("RecoHI.HiEvtPlaneAlgos.hiEvtPlaneFlat_cfi")

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '103X_dataRun2_Prompt_v2', '')
process.GlobalTag.snapshotTime = cms.string("9999-12-31 23:59:59.000")
process.GlobalTag.toGet.extend([
    cms.PSet(record = cms.string("HeavyIonRcd"),
        tag = cms.string("CentralityTable_HFtowers200_DataPbPb_periHYDJETshape_run2v1033p1x01_offline"),
        connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS"),
        label = cms.untracked.string("HFtowers")
        ),
    ])


process.load('RecoHI.HiCentralityAlgos.HiCentrality_cfi')
process.load("RecoHI.HiCentralityAlgos.CentralityBin_cfi")
process.centralityBin.Centrality = cms.InputTag("hiCentrality")
process.centralityBin.centralityVariable = cms.string("HFtowers")

process.load('HeavyIonsAnalysis.Configuration.hfCoincFilter_cff')
process.load('HeavyIonsAnalysis.Configuration.collisionEventSelection_cff')
process.load('RecoHI.HiCentralityAlgos.CentralityFilter_cfi')

if ivars.aodType == 'AOD':
	process.eventSelection = cms.Sequence(
		process.primaryVertexFilter
		* process.hfCoincFilter2Th4
		* process.clusterCompatibilityFilter
   	 )

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.MessageLogger.cerr.FwkReport.reportEvery=1000

process.CondDB.connect = "sqlite_file:"+ivars.dbfile
process.PoolDBESSource = cms.ESSource("PoolDBESSource",
                                       process.CondDB,
                                       toGet = cms.VPSet(cms.PSet(record = cms.string('HeavyIonRPRcd'),
#                                                                  tag = cms.string('HeavyIonRPRcd_PbPb2018_offline')
                                                                  tag = cms.string('HeavyIonRPRcd')
                                                                  )
                                                         )
                                      )
process.es_prefer_flatparms = cms.ESPrefer('PoolDBESSource','')


import FWCore.PythonUtilities.LumiList as LumiList
goodLumiSecs = LumiList.LumiList(filename = ivars.lumifile ).getCMSSWString().split(',')

if ivars.aodType == 'AOD':
    process.source = cms.Source ("PoolSource",
                                 fileNames = cms.untracked.vstring(
            'root://cmsxrootd.fnal.gov//store/hidata/HIRun2018A/HIMinimumBias1/AOD/04Apr2019-v1/610007/F873AB58-6232-974D-9CDB-3BFB1504B449.root',
            'root://cmsxrootd.fnal.gov//store/hidata/HIRun2018A/HIMinimumBias1/AOD/04Apr2019-v1/610007/F7C4BAFB-F443-6C4C-8FFF-B2C89EA3A776.root',
            'root://cmsxrootd.fnal.gov//store/hidata/HIRun2018A/HIMinimumBias1/AOD/04Apr2019-v1/610007/F6200B99-E688-8E47-8301-6FB2D0521021.root'
            ),
                                 inputCommands=cms.untracked.vstring(
            'keep *',
            'drop *_hiEvtPlane_*_*'
            )
                                 )

elif ivars.aodType == 'TestAOD':
    process.source = cms.Source ("PoolSource",
                                 fileNames = cms.untracked.vstring(
            'file:'+ivars.repFile),
                                 inputCommands=cms.untracked.vstring(
            'keep *',
            'drop *_hiEvtPlane_*_*'
            )
                                 )

elif ivars.aodType == 'MiniAOD':
    process.source = cms.Source ("PoolSource",
                                 fileNames = cms.untracked.vstring(
            'file:'+ivars.repFile),
                                 inputCommands=cms.untracked.vstring(
            'keep *',
            'drop *_hiEvtPlane_*_*'
            )
                                 )

if ivars.aodType == 'AOD':
    process.TFileService = cms.Service("TFileService",
                                       fileName = cms.string(ivars.checkfile)
                                       )

if ivars.aodType == 'TestAOD':
    process.TFileService = cms.Service("TFileService",
                                       fileName = cms.string(ivars.checkfile)
                                       )

if ivars.aodType == 'MiniAOD':
    process.TFileService = cms.Service("TFileService",
                                       fileName = cms.string(ivars.checkfile)
                                       )


process.dump = cms.EDAnalyzer("EventContentAnalyzer")

process.hiEvtPlane.trackTag = cms.InputTag("generalTracks")
process.hiEvtPlane.vertexTag = cms.InputTag("offlinePrimaryVertices")
process.hiEvtPlaneFlat.vertexTag = cms.InputTag("offlinePrimaryVertices")
if ivars.aodType == 'MiniAOD':
    process.hiEvtPlane.trackTag = cms.InputTag("packedPFCandidates")
    process.hiEvtPlane.vertexTag = cms.InputTag("offlineSlimmedPrimaryVertices")
    process.hiEvtPlaneFlat.vertexTag = cms.InputTag("offlineSlimmedPrimaryVertices")

process.hiEvtPlane.loadDB = cms.bool(True)
process.hiEvtPlaneFlat.centralityVariable=process.hiEvtPlane.centralityVariable
process.hiEvtPlaneFlat.vertexTag=process.hiEvtPlane.vertexTag
process.hiEvtPlaneFlat.minvtx=process.hiEvtPlane.minvtx
process.hiEvtPlaneFlat.maxvtx=process.hiEvtPlane.maxvtx
process.hiEvtPlaneFlat.flatnvtxbins=process.hiEvtPlane.flatnvtxbins
process.hiEvtPlaneFlat.latminvtx=process.hiEvtPlane.flatminvtx
process.hiEvtPlaneFlat.flatdelvtx=process.hiEvtPlane.flatdelvtx
process.hiEvtPlaneFlat.FlatOrder=process.hiEvtPlane.FlatOrder
process.hiEvtPlaneFlat.CentBinCompression=process.hiEvtPlane.CentBinCompression
process.hiEvtPlaneFlat.caloCentRef=process.hiEvtPlane.caloCentRef
process.hiEvtPlaneFlat.caloCentRefWidth=process.hiEvtPlane.caloCentRefWidth

process.checkflattening.centralityVariable=process.hiEvtPlane.centralityVariable
process.checkflattening.vertexTag=process.hiEvtPlane.vertexTag
process.checkflattening.minvtx=process.hiEvtPlane.minvtx
process.checkflattening.maxvtx=process.hiEvtPlane.maxvtx
process.checkflattening.flatnvtxbins=process.hiEvtPlane.flatnvtxbins
process.checkflattening.latminvtx=process.hiEvtPlane.flatminvtx
process.checkflattening.flatdelvtx=process.hiEvtPlane.flatdelvtx
process.checkflattening.FlatOrder=process.hiEvtPlane.FlatOrder
process.checkflattening.CentBinCompression=process.hiEvtPlane.CentBinCompression
process.checkflattening.caloCentRef=process.hiEvtPlane.caloCentRef
process.checkflattening.caloCentRefWidth=process.hiEvtPlane.caloCentRefWidth

if ivars.aodType == 'AOD':
    process.p = cms.Path(process.offlinePrimaryVerticesRecovery*process.eventSelection*process.centralityBin* process.hiEvtPlane * process.hiEvtPlaneFlat*process.checkflattening)

if ivars.aodType == 'TestAOD':
    process.p = cms.Path(process.centralityBin* process.hiEvtPlane * process.hiEvtPlaneFlat*process.checkflattening)

if ivars.aodType == 'MiniAOD' :
    process.p = cms.Path(process.hiEvtPlane*process.hiEvtPlaneFlat*process.checkflattening)


from HLTrigger.Configuration.CustomConfigs import MassReplaceInputTag
if ivars.aodType=='AOD':
    process = MassReplaceInputTag(process,"offlinePrimaryVertices","offlinePrimaryVerticesRecovery")
    process.offlinePrimaryVerticesRecovery.oldVertexLabel = "offlinePrimaryVertices"
    
if ivars.aodType == 'MiniAOD':
    process = MassReplaceInputTag(process,"offlinePrimaryVertices","offlineSlimmedPrimaryVertices")
