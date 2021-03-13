#!/bin/bash
#======================================
#
# This script runs through the steps needed to create a new event plane
# calibration.  A new calibration is required whenever a change is made
# to the header file
#    RecoHI/HiEvtPlaneAlgos/interface/HiEvtPlaneList.h
# and whenever a change is made to one of the event plane parameters, such
# the pseudorapdity or pt rangle. (That is, ANY change to the default
# parameters found in the 
#    RecoHI/HiEvtPlaneAlgos/python/HiEvtPlane_cfi.py 
# or
#    RecoHI/HiEvtPlaneAlgos/python/hiEvtPlaneFlat_cfi.py
# file. (Note that these two python files MUST have common default values.)
#
# For most calibrations it will be necessary to handle Steps 1 and 4 by submitting crab jobs.
# Sample crab submission scripts are also found supplied in this directory:
# crabSubmit_calib   (for Step 1)
# crabSubmit_check   (for Step 4)

#=======================================

#=======================================
#
#  STEP 1.  Perform an initial replay of the dataset being calibrated. For
#           this sample calibration, three files from
#               /HIRun2018A/HIMinimumBias1/AOD/04Apr2019-v1
#           are replayed.   This replay will create a root file
#           called calib.root containing the data needed for subsequent
#           calibration steps.
#
#========================================

echo  ===================================================================
echo  ">>Step 0.  Several files are created in running this script.  These can"
echo  ">>         be quite large, depending on how many events are analyzed to"
echo  ">>         create the calibration.   By default, the files will be created"
echo  ">>         in your working directory (pwd):"
pwd
echo  ">>         If you would like to use a different location for these file,"
echo  ">>         enter it here:${NC}"
echo  ===================================================================
echo  "  "
str="Directory to store generated files (pwd):"
echo  -n $str
read defloc
if [ -z $defloc ]; then defloc="./"; fi
echo "Base directory set to: "$defloc
echo  ===================================================================
echo  ">>Step 1.  Create the calib.root file with the data needed for the subsequent"
echo  ">>         calibration steps.  Three options are given for the data to be replayed:"
echo  ">>         "
echo  ">>         AOD:  Three /HIRun2018A/HIMinimumBias1/AOD/04Apr2019-v1 dataset files."
echo  ">>         TestAOD:  A single AOD file selected by the AODTEST environment variable."
echo  ">>         MiniAOD:  A single MiniAOD file selected by the MINITEST environment variable."
echo  ">>         "
echo  ">>         Since the replay accesses the" 
echo  ">>         CMS database you need to first issue the command:"
echo  ">>         voms-proxy-init cms"
echo  ">>         The code echos the parameters being assumed for the"
echo  ">>         replay.  Patience might be needed...  No additional input will be requested"
echo  ">>         by this script."
echo  ==================================================================
echo  "  "
str="Replay type (AOD):"
echo -n $str
read aodtype
if [ -z $aodtype ]; then aodtype="AOD"; fi
echo "Entered:"$aodtype
if [ $aodtype = "AOD" ] ; then
    echo "AOD type selected"
    infile=''
elif [ $aodtype = "TestAOD" ] ; then
    echo "TestAOD type selected"
    if [ -z $AODTEST ]; then
	echo "The global parameter AODTEST has not been set."
	echo "To do this from a BASH shell, issue the command:"
	echo "export AODTEST={AOD file}"
	exit
    else
	echo "Replay will be from the file: "$AODTEST
	infile=$AODTEST
    fi
elif [ $aodtype = "MiniAOD" ] 
then
    echo "MiniAOD type selected"
    if [ -z $MINITEST ]; then
	echo "The global parameter MINITEST has not been set."
	echo "To do this from a BASH shell, issue the command:"
	echo "export MINITEST={AOD file}"
	exit
    else
	echo "Replay will be from the file: "$MINITEST
	infile=$MINITEST
    fi
else
    echo "Only allowed options are AOD|TestAOD|MiniAOD"
    exit
fi

echo voms-proxy-init -voms cms
voms-proxy-init -voms cms
COM="cmsRun calibtree_cfg.py outfile="$defloc"/calib.root repFile="$infile" aodType="$aodtype 
echo  $COM
$COM

echo  ===================================================================
echo  ">>Step 2.  Generate the event plane recentering/flattening parameters"
echo  ">>         This is done with a standalone program that takes the"
echo  ">>         calib.root file generated in Step 1 as input."
echo  ">> "
echo  ">>         Although, to keep this script simple, we only have one input file for"
echo  ">>         this step, in general one would expect many files with one file generated for"
echo  ">>         each crab job.  The list of files to be used in the calibration"
echo  ">>         is specified in temphi.lis ."
echo  ">> "
echo  ">>         This script is set up to handle multiple IOVs based on run number."
echo  ">>         However, here only one IOV is defined, for runs 1 through 328000. "
echo  ">>         The IOV list must start with 1,  but additional ranges can be defined."
echo  ">>         For example, in working with the entire 2018 PbPb dataset, the list is"
echo  ">>         declared with:"
echo  ">>         declare -a list=(1 326545 326620 326887 327147 327230 328000)"
echo  ==================================================================
echo  " "       

cd EPCalib
[ -h HiEvtPlaneList.h ] && rm -f HiEvtPlaneList.h
[ -f HiEvtPlaneList.h ] && rm -f HiEvtPlaneList.h
ln -s $CMSSW_BASE/src/RecoHI/HiEvtPlaneAlgos/interface/HiEvtPlaneList.h 
[ -h HiEvtPlaneFlatten.h ] && rm -f HiEvtPlaneFlatten.h
[ -f HiEvtPlaneFlatten.h ] && rm -f HiEvtPlaneFlatten.h
ln -s $CMSSW_BASE/src/RecoHI/HiEvtPlaneAlgos/interface/HiEvtPlaneFlatten.h
cd ..
[ -d RescorTables ] && rm -rf RescorTables
calfile=$defloc"/calib.root"
ls -1 $calfile > tmphi.lis
echo "Listing of tmphi.lis:"
cat tmphi.lis
declare -a list=(1 328000)
nbreaks=${#list[@]}
echo $nbreaks
for (( i=0; i<${nbreaks}-1; i++));
do
min=${list[$i]}
max=${list[$i+1]}
max=$((max-1))
minrun=$min
maxrun=$max
range=$minrun
range+='_'
range+=$maxrun 
resdir=$defloc"/RescorTables"
[ ! -d $resdir ] && mkdir $resdir
resdir=$defloc"/RescorTables/Rescor_"$range
[ -d $resdir ] && rm -rf $resdir
mkdir $resdir
offfile=$defloc"/offset_"$range".root"
echo $offfile
[ -f $offfile ] && rm $offfile
tmpfile=$defloc"/tmp_"$range".root"
echo $tmpfile
[ -f $tmpfile ] && rm $tmpfile
rpflat=$defloc"/rpflat_"$range".root"
echo $rpflat
[ -f $rpflat ] && rm $rpflat
epfile=$defloc"/ep_"$range".root"
echo $epfile
[ -f $epfile ] && rm $epfile
arg='EPCalib/EPCalib.C+('$minrun','$maxrun',"tmphi.lis","'$tmpfile'","'$epfile'","'$offfile'","'$resdir'")'
echo $arg
root -l -b -q $arg
echo ">>The following files/directories should now have been created:"
echo $resdir'   -- Directory containing the event plane resolutions'
echo $rpflat'   -- File with results of the flattening operation'
echo $offfile'   --File with offsets that can be used in a track-by-track correction'
[ -f $tmpfile ] && rm $tmpfile

echo  ===================================================================
echo  " "
echo  "Step 3.  Move calibration to database file"
echo  " "
echo  ===================================================================

ln -s $epfile rpflat_combined.root
move='cmsRun moveflatparamstodb_cfg.py print outputFile=HeavyIonRPRcd_'$range'.db outtag=HeavyIonRPRcd begin='$minrun' end='$maxrun' rescorloc='$resdir' infile='$epfile
echo $move
$move
[ -f EPCalib/EPCalib_C.d ] && rm EPCalib/EPCalib_C.d
[ -f EPCalib/EPCalib_C.so ] && rm EPCalib/EPCalib_C.so
[ -f EPCalib/EPCalib_C_ACLiC_dict_rdict.pcm ] && rm EPCalib/EPCalib_C_ACLiC_dict_rdict.pcm
rm -rf rpflat_combined.root

conddb_import -f sqlite_file:HeavyIonRPRcd_$range.db -c sqlite_file:HeavyIonRPRcd_offline.db -i HeavyIonRPRcd -t HeavyIonRPRcd -b $minrun -e $maxrun
[ -f HeavyIonRPRcd_$range.db ] && rm HeavyIonRPRcd_$range.db
done
echo ===================================================================
echo ">> "
echo ">>The final calibration file, containing the calibrations for the different IOVs, is called"
echo ">>HeavyIonRPRcd_offline.db"
echo ">> "
echo ===================================================================
[ -f tmphi.lis ] && rm tmphi.lis

echo  ===================================================================
echo  ">> "
echo  ">>Step 4.  Check that everything works.   The new calibration is used to"
echo  ">>         replay the raw data a second time, now with the flattening being done."
echo  ">>         A final root program generates several histograms compaing the input"
echo  ">>         data and final results.   The original (black) histograms should be"
echo  ">>         completed covered by the final (red) histograms.  ANY black showing would indicated"
echo  ">>         a potential problem."
echo  ">> "
echo  ===================================================================
COM="cmsRun checkep_cfg.py checkfile="$defloc"/check.root repFile="$infile" aodType="$aodtype
echo $COM
$COM
calibFile=$defloc"calib.root"
moveFile=$epfile
checkFile=$defloc"/check.root"
root -l -b -q  'compare.C("'$calibFile'","'$moveFile'","'$checkFile'")'
#[ -f $epfile ] && rm $epfile

