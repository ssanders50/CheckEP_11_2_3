import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
import os
import sys
ivars = VarParsing.VarParsing('analysis')

ivars.register('lumifile',
                'Cert_326381-327564_HI_PromptReco_Collisions18_JSON.txt',
		VarParsing.VarParsing.multiplicity.singleton,
		VarParsing.VarParsing.varType.string,
                "lumi file")

ivars.register('outfile',
               'calib.root',
		VarParsing.VarParsing.multiplicity.singleton,
		VarParsing.VarParsing.varType.string,
                "output file name")

ivars.register ('aodType',
                'AOD',
                mult=ivars.multiplicity.singleton,
                mytype=ivars.varType.string,
                info="AOD/TestAOD/MiniAOD")

ivars.register ('repFile',
                'infile.root',
                mult=ivars.multiplicity.singleton,
                mytype=ivars.varType.string,
                info="AOD/TestAOD/MiniAOD")


ivars.parseArguments()

process = cms.Process("FlatCalib")

process.load('Configuration.StandardSequences.Services_cff')
process.load("CondCore.CondDB.CondDB_cfi")
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
if ivars.aodType == 'AOD':
	process.load("RecoVertex.PrimaryVertexProducer.OfflinePrimaryVerticesRecovery_cfi")
	process.load('HeavyIonsAnalysis.EventAnalysis.clusterCompatibilityFilter_cfi')
	process.load("HeavyIonsAnalysis.Configuration.hfCoincFilter_cff")
	process.load("HeavyIonsAnalysis.Configuration.analysisFilters_cff")
	process.load('HeavyIonsAnalysis.EventAnalysis.skimanalysis_cfi')
	process.load('HeavyIonsAnalysis.Configuration.collisionEventSelection_cff')
	process.load('RecoHI.HiCentralityAlgos.CentralityFilter_cfi')

	process.eventSelection = cms.Sequence(
		process.primaryVertexFilter
		* process.hfCoincFilter2Th4
		* process.clusterCompatibilityFilter
    	)
process.load("HeavyIonsAnalysis.HiEvtPlaneCalib.checkflattening_cfi")

process.load("RecoHI.HiEvtPlaneAlgos.HiEvtPlane_cfi")
process.load("HeavyIonsAnalysis.HiEvtPlaneCalib.evtplanecalibtree_cfi")

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


process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

import FWCore.PythonUtilities.LumiList as LumiList
goodLumiSecs = LumiList.LumiList(filename = ivars.lumifile ).getCMSSWString().split(',')

readiles = cms.untracked.vstring()
secFiles = cms.untracked.vstring() 

process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(),
                            inputCommands=cms.untracked.vstring(
        'keep *',
        'drop *_hiEvtPlane_*_*'
        ),
                            dropDescendantsOfDroppedBranches=cms.untracked.bool(False)
                            )
if ivars.aodType == 'AOD':
    process.source = cms.Source ("PoolSource",fileNames = cms.untracked.vstring(
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

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(ivars.outfile)
)
if ivars.aodType == 'MiniAOD':
    process.hiEvtPlane.trackTag = cms.InputTag("packedPFCandidates")
    process.hiEvtPlane.vertexTag = cms.InputTag("offlineSlimmedPrimaryVertices")
 
process.dump = cms.EDAnalyzer("EventContentAnalyzer")
process.evtPlaneCalibTree.centralityVariable = process.hiEvtPlane.centralityVariable
process.evtPlaneCalibTree.centralityBinTag = process.hiEvtPlane.centralityBinTag
process.evtPlaneCalibTree.vertexTag = process.hiEvtPlane.vertexTag
process.evtPlaneCalibTree.caloTag = process.hiEvtPlane.caloTag
process.evtPlaneCalibTree.castorTag = process.hiEvtPlane.castorTag
process.evtPlaneCalibTree.trackTag = process.hiEvtPlane.trackTag
process.evtPlaneCalibTree.lostTag = process.hiEvtPlane.lostTag
process.evtPlaneCalibTree.chi2MapTag = process.hiEvtPlane.chi2MapTag
process.evtPlaneCalibTree.chi2MapLostTag = process.hiEvtPlane.chi2MapLostTag
process.evtPlaneCalibTree.nonDefaultGlauberModel = process.hiEvtPlane.nonDefaultGlauberModel
process.evtPlaneCalibTree.loadDB = process.hiEvtPlane.loadDB
process.evtPlaneCalibTree.minet = process.hiEvtPlane.minet
process.evtPlaneCalibTree.maxet = process.hiEvtPlane.maxet
process.evtPlaneCalibTree.minpt = process.hiEvtPlane.minpt
process.evtPlaneCalibTree.minvtx = process.hiEvtPlane.minvtx
process.evtPlaneCalibTree.maxvtx = process.hiEvtPlane.maxvtx
process.evtPlaneCalibTree.flatnvtxbins = process.hiEvtPlane.flatnvtxbins
process.evtPlaneCalibTree.flatminvtx = process.hiEvtPlane.flatminvtx
process.evtPlaneCalibTree.flatdelvtx = process.hiEvtPlane.flatdelvtx
process.evtPlaneCalibTree.dzdzerror = process.hiEvtPlane.dzdzerror
process.evtPlaneCalibTree.d0d0error = process.hiEvtPlane.d0d0error
process.evtPlaneCalibTree.pterror = process.hiEvtPlane.pterror
process.evtPlaneCalibTree.chi2perlayer = process.hiEvtPlane.chi2perlayer
process.evtPlaneCalibTree.dzdzerror_pix = process.hiEvtPlane.dzdzerror_pix
process.evtPlaneCalibTree.chi2 = process.hiEvtPlane.chi2
process.evtPlaneCalibTree.nhitsValid = process.hiEvtPlane.nhitsValid
process.evtPlaneCalibTree.FlatOrder = process.hiEvtPlane.FlatOrder
process.evtPlaneCalibTree.NumFlatBins = process.hiEvtPlane.NumFlatBins
process.evtPlaneCalibTree.caloCentRef = process.hiEvtPlane.caloCentRef
process.evtPlaneCalibTree.caloCentRefWidth = process.hiEvtPlane.caloCentRefWidth
process.evtPlaneCalibTree.CentBinCompression = process.hiEvtPlane.CentBinCompression
process.evtPlaneCalibTree.cutEra = process.hiEvtPlane.cutEra

process.hiEvtPlane.loadDB = cms.bool(False)

if ivars.aodType == 'AOD':
    process.p = cms.Path(process.offlinePrimaryVerticesRecovery*process.eventSelection*process.centralityBin*process.hiEvtPlane * process.evtPlaneCalibTree  )

if ivars.aodType == 'TestAOD':
    process.p = cms.Path(process.centralityBin*process.hiEvtPlane * process.evtPlaneCalibTree  )

if ivars.aodType == 'MiniAOD':
    process.p = cms.Path(process.hiEvtPlane * process.evtPlaneCalibTree  )


from HLTrigger.Configuration.CustomConfigs import MassReplaceInputTag
if ivars.aodType=='AOD':
    process = MassReplaceInputTag(process,"offlinePrimaryVertices","offlinePrimaryVerticesRecovery")
    process.offlinePrimaryVerticesRecovery.oldVertexLabel = "offlinePrimaryVertices"

    
if ivars.aodType == 'MiniAOD':
    process = MassReplaceInputTag(process,"offlinePrimaryVertices","offlineSlimmedPrimaryVertices")
