# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% [markdown]
# # OSI Lat Long
# ### This Notebook uses the XY of the point featureclass and adds Lat Long to each related row in a related table. The FeederID (aka Circuit Number) is also determined for Electric features.
# A CSV file is generated that will be used to support a seperate project.
# 
# The second half of the Notebook explores the electric consumption data with a [SpatialDataFrame](https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.features.toc.html?highlight=spatialdataframe#spatialdataframe) using the customers table modifed in the first half.
#%% [markdown]
# W/WW notes: needs GloabID in customer account tables
# 
# Run Feeder Manager First, then extract for OSI

#%%
import arcpy
import numpy as np
import pandas as pd
#test commit


#%%
gdb = "C:/Users/friendde/Documents/ArcGIS/Projects/OSILatLong/OSILatLong.gdb"
gdb_electric = "C:/Users/friendde/Documents/ArcGIS/Projects/OSILatLong/OSILatLong.gdb/Electric"
osiExtract = "C:/Users/friendde/Documents/ArcGIS/Projects/OSILatLong/OSI_Electric_Extract.gdb"
osiExtract_electric = "C:/Users/friendde/Documents/ArcGIS/Projects/OSILatLong/OSI_Electric_Extract.gdb/Electric"
#omsRegion = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\eRegion"
#omsRegionSource = r"C:\GISData\Data\Snapshot\mxElectric.geodatabase\main.Electric\main.EDEngDistrict"
omsRegion = "C:/Users/friendde/Documents/ArcGIS/Projects/OSILatLong/OSILatLong.gdb/EDEngDistrict"
sourceGDBList = ["C:/arcdata/Gas_Extract.gdb","C:/arcdata/WWW_Extract.gdb/"]

esvcPntDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\eServicePoint"
gsvcPntDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\gMeterSet"
rsvcPntDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\rServicePoint"
wsvcPntDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\ServicePoint"
svcPntDestList = [esvcPntDest,gsvcPntDest,rsvcPntDest,wsvcPntDest]

#svcPntDict = {esvcPntSource:esvcPntDest,gsvcPntSource:gsvcPntDest,rsvcPntSource:rsvcPntDest,wsvcPntSource:wsvcPntDest}

ecustAcctSource = "C:/Users/friendde/Documents/ArcGIS/Projects/OSILatLong/OSI_Electric_Extract.gdb/eCUSTOMERACCOUNT"
gcustAcctSource = "C:/arcdata/Gas_Extract.gdb/gCUSTOMERACCOUNT"
rcustAcctSource = "C:/arcdata/WWW_Extract.gdb/rCustomerAccount"
wcustAcctSource = "C:/arcdata/WWW_Extract.gdb/wCustomerAccount"
custAcctSourceList = [ecustAcctSource,gcustAcctSource,rcustAcctSource,wcustAcctSource]

ecustAcctDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\eCUSTOMERACCOUNT"
gcustAcctDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\gCUSTOMERACCOUNT"
rcustAcctDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\rCUSTOMERACCOUNT"
wcustAcctDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\wCUSTOMERACCOUNT"
custAcctDestList = [ecustAcctDest,gcustAcctDest,rcustAcctDest,wcustAcctDest]

custAcctDict = {ecustAcctSource:ecustAcctDest,gcustAcctSource:gcustAcctDest,rcustAcctSource:rcustAcctDest,wcustAcctSource:wcustAcctDest}

electFields = ["PHASEDESIGNATION","FEEDERID","TRANSFORMERBANKOBJECTID","eTransformerBank_GLOBALID","RegionName"]
svcPntDestFlds = ["OID@","GLOBALID","POINT_X","POINT_Y","PHASEDESIGNATION","FEEDERID","TRANSFORMERBANKOBJECTID","eTransformerBank_GLOBALID","RegionName"]
custAcctDestFlds = ["SERVICEPOINTOBJECTID","GLOBALID","POINT_X","POINT_Y","PHASEDESIGNATION","FeederID","Utility","TRANSFORMERBANKOBJECTID","eTransformerBank_GLOBALID","RegionName"]
custAcctOutFlds = ["OID@","SvcPntOID","INSTALL_NUM","POINT_X","POINT_Y","PHASEDESIGNATION","FeederID","TRANSFORMERBANKOBJECTID","eTransformerBank_GLOBALID","RegionName"]
custAnalysis = ["SERVICEPOINTOBJECTID","INSTALL_NUM","POINT_X","POINT_Y","AVGCONSUMPTION","MAXCONSUMPTION"]
custLocations = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\CustomerLocations"
custAcctFile = r'C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\GIS.csv'

#feature classes that System Control does not want in OMS extract
fcDelete = ['eAbandondedPriUGCond','eAbandonedSecUGCond','eCircuitMapGrid','eCircuitMapGrid2x3','eComments',
           'eControlCommunication','eDownGuy','eLight','eSpanGuy','eHyperlink']
elecGUIDS = ['']

rc_list = []

#regions = ['SE', 'SW Main St to 34 St', 'NW Main St to 34 St', 'SW west of I-75', 'SW 34 St to I-75', 'NW west of I-75', 'NW to 39 Ave, 34 Ave to I-75', 'NW north of 39 Ave', 'NE']
regions = ['East','West']
expression = "updateRegion(region)"
codeblock = """
def updateRegion(name):
    return str(name)"""

#%% [markdown]
# #### Phase Translation between ArcFM and OSI
# | Phase | ArcFM | OSI |
# |-------|-------|-----|
# |   A   |   4   |  1  ||
# |   B   |   2   |  2  |
# |   C   |   1   |  3  |
# |   AB  |   6   |  12 |
# |   AC  |   5   |  13 |
# |   BC  |   3   |  23 |
# |   ABC |   7   |  123|

#%%
# convert ArcFM Phase to OSI Phase
def getPhaseDesignation(phaseDesignation):
    if phaseDesignation is None:
        ph = 0
        return ph
    if phaseDesignation == 1:
        ph = 3
        return ph
    if phaseDesignation == 2:
        ph = 2
        return ph
    if phaseDesignation == 3:
        ph = 23
        return ph
    if phaseDesignation == 4:
        ph = 1
        return ph
    if phaseDesignation == 5:
        ph = 13
        return ph
    if phaseDesignation == 6:
        ph = 12
        return ph
    if phaseDesignation == 7:
        ph = 123
        return ph

def gettxOID(txOID):
    if txOID is None:
        txOID = 0
        return txOID
    else:
        return txOID

def gettxGUID(txGUID):
    print(f'in gettxGUID')
    if txGUID is None:
        print(f'txGUID is {txGUID}')
        txGUID = 0
        return txGUID
    else:
        print(f'txGUID is {txGUID}')
        return txGUID

def replaceChar(strReplace):
    replaceList = [' ',',','-']
    for r in replaceList:
        if r in (strReplace):
            strReplace = strReplace.replace(r,'')

    return strReplace

def listReplace(lst, _from, _to):
   return([_to if v == _from else v for v in lst])


#%%
# convert ObjectID relationship to GlobalID relationship in Electric Feature Class
# exclude from list
#include = ['eTransformerBank_ServicePoint']
arcpy.env.workspace = osiExtract
rcList = [c.name for c in arcpy.Describe(osiExtract_electric).children if c.datatype == "RelationshipClass"]
rcList


#%%
for rc in rcList:
    print(f'Migrating {rc}\n')    
    desc = arcpy.Describe(rc)
    print("%-25s %s" % ("Backward Path Label:", desc.backwardPathLabel))
    print("%-25s %s" % ("Cardinality:", desc.cardinality))
    print("%-25s %s" % ("Class key:", desc.classKey))
    print("%-25s %s" % ("Destination Class Names:", desc.destinationClassNames))
    print("%-25s %s" % ("Forward Path Label:", desc.forwardPathLabel)) 
    print("%-25s %s" % ("Is Attributed:", desc.isAttributed))
    print("%-25s %s" % ("Is Composite:", desc.isComposite)) 
    print("%-25s %s" % ("Is Reflexive:", desc.isReflexive))
    print("%-25s %s" % ("Key Type:", desc.keyType))
    print("%-25s %s" % ("Notification Direction:", desc.notification))
    print("%-25s %s" % ("Origin Class Names:", desc.originClassNames))
    print("\n")
    arcpy.MigrateRelationshipClass_management(rc)


#%%
# convert ObjectID relationship to GlobalID relationship in root osiExtract
# exclude from list
exclude = ['CircuitBreaker_CircuitSource','eConduitBank_eConduitBankConfigDef','eSurfaceStructure__ATTACHREL_1',
          'eSupportStructure__ATTACHREL_1','SuppStructure_ForeignAttach','gCustomeraccount_SAPInstallation',
          'gGasValve_gValveInspection','gGasValve_gValveMaintenance','gEmergencyShutoff_gEMSValves',
           'gAbandonedValve_gValveInspection','eCUSTOMERACCOUNT__ATTACHREL'
          ]
include = ['ServicePt_CustomerAcct']
rcList = [c.name for c in arcpy.Describe(osiExtract).children if c.datatype == "RelationshipClass"]
#rc_List = []
for rc in rcList:
    if rc in include:
        #print(f'Appending {rc} to rc_list')
        rc_list.append(rc)
        print(f'Migrating {rc}\n')
        desc = arcpy.Describe(rc)
        print("%-25s %s" % ("Backward Path Label:", desc.backwardPathLabel))
        print("%-25s %s" % ("Cardinality:", desc.cardinality))
        print("%-25s %s" % ("Class key:", desc.classKey))
        print("%-25s %s" % ("Destination Class Names:", desc.destinationClassNames))
        print("%-25s %s" % ("Forward Path Label:", desc.forwardPathLabel)) 
        print("%-25s %s" % ("Is Attributed:", desc.isAttributed))
        print("%-25s %s" % ("Is Composite:", desc.isComposite)) 
        print("%-25s %s" % ("Is Reflexive:", desc.isReflexive))
        print("%-25s %s" % ("Key Type:", desc.keyType))
        print("%-25s %s" % ("Notification Direction:", desc.notification))
        print("%-25s %s" % ("Origin Class Names:", desc.originClassNames))
        print("\n")
        arcpy.MigrateRelationshipClass_management(rc)
    else:
        pass


#%%
# change wksp to gdb
arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)


#%%
# delete all existing tables in workspace, new tables are created or copied in
fdsList = arcpy.ListDatasets()
for fds in fdsList:
    print(f'Deleting {fds}')
    arcpy.Delete_management(fds)
tblList = arcpy.ListTables()
for tbl in tblList:
    print(f'Deleting {tbl}')
    arcpy.Delete_management(tbl)
fcsList = arcpy.ListFeatureClasses()
for fcs in fcsList:
    if fcs == 'EDEngDistrict':
        pass
    else:
        print(f'Deleting {fcs}')
        arcpy.Delete_management(fcs)


#%%
# delete specific tables System Control does not want in OMS extract
arcpy.env.workspace = osiExtract

datasets = arcpy.ListDatasets(feature_type='feature')
datasets = [''] + datasets if datasets is not None else []

for ds in datasets:
    for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
        #print(f'found {fc}')
        if fc in fcDelete:
            print(f'Deleting {fc}')
            arcpy.Delete_management(fc)


#%%
#check for GlobalID before migrating relationship classes
for custAcctSource in custAcctSourceList:
    fldList = [fld.name.upper() for fld in arcpy.Describe(custAcctSource).fields]
    #print(fldList)
    if "GLOBALID" not in fldList:
        print(f'Adding GlobalID to {custAcctSource}')
        arcpy.AddGlobalIDs_management(custAcctSource)


#%%
# convert ObjectID relationship to GlobalID relationship in root sourceGDBList
# exclude from list
exclude = ['CircuitBreaker_CircuitSource','eConduitBank_eConduitBankConfigDef','eSurfaceStructure__ATTACHREL_1',
          'eSupportStructure__ATTACHREL_1','SuppStructure_ForeignAttach','gCustomeraccount_SAPInstallation',
          'gGasValve_gValveInspection','gGasValve_gValveMaintenance','gEmergencyShutoff_gEMSValves',
           'gAbandonedValve_gValveInspection','eCUSTOMERACCOUNT__ATTACHREL'
          ]
include = ['gMeterSet_gCustomerAccount','RSERVICEPOINT_CUSTACCT','WSERVICEPOINT_CUSTACCT']
for source_gdb in sourceGDBList:
    arcpy.env.workspace = source_gdb
    rcList = [c.name for c in arcpy.Describe(source_gdb).children if c.datatype == "RelationshipClass"]
    for rc in rcList:
        if rc in include:
            rc_list.append(rc)
            print(f'Migrating {rc}\n')
            desc = arcpy.Describe(rc)
            print("%-25s %s" % ("Backward Path Label:", desc.backwardPathLabel))
            print("%-25s %s" % ("Cardinality:", desc.cardinality))
            print("%-25s %s" % ("Class key:", desc.classKey))
            print("%-25s %s" % ("Destination Class Names:", desc.destinationClassNames))
            print("%-25s %s" % ("Forward Path Label:", desc.forwardPathLabel)) 
            print("%-25s %s" % ("Is Attributed:", desc.isAttributed))
            print("%-25s %s" % ("Is Composite:", desc.isComposite)) 
            print("%-25s %s" % ("Is Reflexive:", desc.isReflexive))
            print("%-25s %s" % ("Key Type:", desc.keyType))
            print("%-25s %s" % ("Notification Direction:", desc.notification))
            print("%-25s %s" % ("Origin Class Names:", desc.originClassNames))
            print("\n")
            arcpy.MigrateRelationshipClass_management(rc)
        else:
            pass


#%%
# copy in custAcctDict customer tables into workspace
# add fields not normaly in customer tables
arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True
for k,v in custAcctDict.items():
    print(f'Copying {k} to {v}')
    arcpy.Copy_management(k,v)
    if arcpy.Exists(v):
        #print(f'Copy Success {v}')
        #field_names = [f.name for f in arcpy.ListFields(v)]
        arcpy.AddField_management(v, "POINT_X", "DOUBLE")
        arcpy.AddField_management(v, "POINT_Y", "DOUBLE")
        arcpy.AddField_management(v, "PHASEDESIGNATION", "LONG")
        arcpy.AddField_management(v, "SERVICEPOINTOBJECTID", "LONG")
        arcpy.AddField_management(v, "Utility", "TEXT")
        arcpy.AddField_management(v, "FeederID", "TEXT")
        arcpy.AddField_management(v, "TRANSFORMERBANKOBJECTID", "LONG")
        arcpy.AddField_management(v, "eTransformerBank_GLOBALID", "GUID")
        arcpy.AddField_management(v, "RegionName", "TEXT")
    else:
        print(f'Copy Failed! {v}')


#%%
#Add Responder Region Name to Service Points (electric only for now)
arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True
try:
    arcpy.AddField_management(esvcPntDest, "RegionName", "TEXT")
    arcpy.MakeFeatureLayer_management(esvcPntDest,'eSvcPnt')
    for region in regions:
        with arcpy.da.SearchCursor(omsRegion,"DirName") as sc:
            print(f"Current Region Name {region}")
            #desc = arcpy.da.Describe(omsRegion)
            #print(f"FIDSet {desc['FIDSet']}")
            #regionName = replaceChar(region)
            #print(f"New Region Name {regionName}")
            arcpy.MakeFeatureLayer_management(omsRegion,region,f"DirName = '{region}'")
            arcpy.CopyFeatures_management(region, gdb + f"/{region}")
            if arcpy.Exists(gdb + f"/{region}"):
                #print(f"found {regionName}")
                arcpy.SelectLayerByLocation_management('eSvcPnt',"",region)
                #result = arcpy.GetCount_management(gdb + "/" + regionName)
                #print(result)
                result = arcpy.GetCount_management('eSvcPnt')
                print(f"{result} meters are within {region}")
                #desc = arcpy.Describe('eSvcPnt')
                #print(desc['FIDSet'])
                #print(len(desc.FIDSet.split(";")))
                if int(result.getOutput(0)) > 0:
                    print(f'Adding {region} to {int(result.getOutput(0))} Service Points')
                    arcpy.CalculateField_management('eSvcPnt',"RegionName",expression,"PYTHON",codeblock)
except:
    print(arcpy.GetMessages(2))
    


#%%
# add XY coords and some electric fields to all service point features
for fc in svcPntDestList:
    if arcpy.Exists(fc):
        print(f'Adding XY to {fc}')
        arcpy.AddXY_management(fc)
        for electField in electFields:
            if len(arcpy.ListFields(fc, electField)):
                print(f'{electField} exists in {fc}')
                pass
            else:                
                print(f'Adding {electField} to {fc}')
                if electField in ["PHASEDESIGNATION","TRANSFORMERBANKOBJECTID"]:
                    arcpy.AddField_management(fc, electField, "LONG")
                elif electField == "eTransformerBank_GLOBALID":
                    arcpy.AddField_management(fc, electField, "GUID")
                else:
                    arcpy.AddField_management(fc, electField, "TEXT")


#%%
edit = arcpy.da.Editor(gdb)
edit.startEditing(False, False)
edit.startOperation()

#%% [markdown]
# rc_list = []
# arcpy.env.workspace = osiExtract
# include = ['ServicePt_CustomerAcct']
# rcList = [c.name for c in arcpy.Describe(osiExtract).children if c.datatype == "RelationshipClass"]
# for rc in rcList:
#     if rc in include:
#         #print(f'Appending {rc} to rc_list')
#         rc_list.append(rc)
# 
# include = ['gMeterSet_gCustomerAccount','RSERVICEPOINT_CUSTACCT','WSERVICEPOINT_CUSTACCT']
# for source_gdb in sourceGDBList:
#     arcpy.env.workspace = source_gdb
#     rcList = [c.name for c in arcpy.Describe(source_gdb).children if c.datatype == "RelationshipClass"]
#     for rc in rcList:
#         if rc in include:
#             rc_list.append(rc)
# rc_list

#%%
arcpy.env.workspace = gdb
exclude_list = ["SAP_INSTALLATION","eCircuitBreaker","eCabinetStructure","eSurfaceStructure", "eSupportStructure",
                "gGasValve","gEmergencyShutoff","eCIRCUITSOURCE","eCUSTOMERACCOUNT__ATTACH",
                "eSurfaceStructure__ATTACH_1","eFOREIGNATTACHMENT","GVALVEINSPECTION","GEMSVALVES"]
for rc in rc_list:
    desc = arcpy.Describe(rc)
    if desc.originClassNames[0] in ["SAP_INSTALLATION","eCircuitBreaker","eCabinetStructure","eSurfaceStructure",
                                    "eSupportStructure","gGasValve","gEmergencyShutoff"]:
        pass
    elif desc.destinationClassNames[0] in ["SAP_INSTALLATION","eCIRCUITSOURCE","eCUSTOMERACCOUNT__ATTACH",
                                           "eSurfaceStructure__ATTACH_1","eFOREIGNATTACHMENT","GVALVEINSPECTION","GEMSVALVES"]:
        pass
    else:
        custAcctFlds = []
        custAcctFlds = listReplace(custAcctDestFlds,"GLOBALID",f"{desc.originClassNames[0]}_GLOBALID")
        with arcpy.da.SearchCursor(desc.originClassNames[0],svcPntDestFlds) as svcpnts:
#["OID@","GLOBALID","POINT_X","POINT_Y","PHASEDESIGNATION","FEEDERID","TRANSFORMERBANKOBJECTID","eTransformerBank_GLOBALID","RegionName"]
            print(f"Searching {desc.originClassNames[0]} and updating {desc.destinationClassNames[0]}")
            for svcpnt in svcpnts:
                whereClause = f"{desc.originClassNames[0]}_GLOBALID = '{svcpnt[1]}'"
                with arcpy.da.UpdateCursor(desc.destinationClassNames[0],custAcctDestFlds,whereClause) as uc:
#["SERVICEPOINTOBJECTID","GLOBALID","POINT_X","POINT_Y","PHASEDESIGNATION","FeederID","Utility","TRANSFORMERBANKOBJECTID","eTransformerBank_GLOBALID","RegionName"]
                    print(f"Updating: {desc.destinationClassNames[0]}")
                    for row in uc:
                        row[0] = svcpnt[0] #SncPntOID
                        #row[1] = svcpnt[1] #GlobalID
                        row[2] = svcpnt[2] #Point_X
                        row[3] = svcpnt[3] #Point_Y
                        row[4] = getPhaseDesignation(svcpnt[4]) #Phase
                        row[5] = svcpnt[5] #FeederID
                        row[6] = desc.destinationClassNames[0][:1] #Utility from CustomerAccount table prefix letter
                        #row[7] = gettxOID(svcpnt[7])
                        row[8] = gettxGUID(svcpnt[7]) #eTx_GlobalID
                        row[9] = svcpnt[8] #RegionName
                        uc.updateRow(row)


#%%
edit.stopOperation()
edit.stopEditing(True)


#%%
arcpy.Delete_management(custLocations)


#%%
arcpy.CreateTable_management(gdb,"CustomerLocations",ecustAcctDest)


#%%
#arcpy.TruncateTable_management(custLocations)


#%%
arcpy.Append_management(custAcctDestList,custLocations,"NO_TEST")


#%%
expression = "setFeeder(!FeederID!)"
codeblock = """
def setFeeder(feeder):
    if feeder is None:
        return 0
    else:
        return feeder"""
arcpy.CalculateField_management(custLocations,"FeederId",expression,"PYTHON3",codeblock)


#%%
expression = "setUnknown(!RegionName!)"
codeblock = """
def setUnknown(r):
    if r is None:
        return "Not Set"
    elif r == 0:
        return "Not Set"
    else:
        return r"""
arcpy.CalculateField_management(custLocations,"RegionName",expression,"PYTHON3",codeblock)


#%%
expression = "setPhase(!PhaseDesignation!)"
codeblock = """
def setPhase(phase):
    if phase is None:
        return 0
    else:
        return phase"""
arcpy.CalculateField_management(custLocations,"PhaseDesignation",expression,"PYTHON3",codeblock)

#%% [markdown]
# ### Use numpy and pandas to export to CSV
# 
# Use arcpy [```TableToNumPyArray()```](http://pro.arcgis.com/en/pro-app/arcpy/data-access/tabletonumpyarray.htm)
# See also [Working with numpy in ArcGIS](http://pro.arcgis.com/en/pro-app/arcpy/get-started/working-with-numpy-in-arcgis.htm)
#%% [markdown]
# TODO - write file to
# \\gruomsdpre04 C:\customer_premise_osi_oms
# \\gruomsdpre05 C:\customer_premise_osi_oms
# \\gruomsdqae06 C:\customer_premise_osi_oms
# \\gruomsdpra14 C:\customer_premise_osi_oms
# \\gruomsppre12 C:\customer_premise_osi_oms
# 
#%% [markdown]
# Ready new numpy array for consumption analysis
#%% [markdown]
# remove empty line at end of CSV

#%%
#nparr = arcpy.da.TableToNumPyArray(custLocations,["ServicePointObjectID","POINT_X","POINT_Y","AVGCONSUMPTION","MAXCONSUMPTION","Utility"],skip_nulls=True)


#%%
nparr = arcpy.da.TableToNumPyArray(custLocations,["ObjectID","INSTALL_NUM","POINT_X","POINT_Y","PHASEDESIGNATION","FeederID","Utility","eTransformerBank_GLOBALID","RegionName"])


#%%
df = pd.DataFrame(nparr)


#%%
df.head()


#%%
df.tail()

#%% [markdown]
# Show only rows with a series filter

#%%
df.loc[(df["Utility"]=="g"), ["ObjectID","INSTALL_NUM","POINT_X","POINT_Y","PHASEDESIGNATION","FeederID","Utility","eTransformerBank_GLOBALID","RegionName"]]


#%%
df.ObjectID


#%%
df = df.astype({'ObjectID':str}, copy=False)


#%%
df.ObjectID


#%%
df.ObjectID = np.where(df.Utility != 'e', df.Utility + df.ObjectID,df.ObjectID)


#%%
df.head()


#%%
df.tail()


#%%
df.loc[(df.Utility == 'e'), ["ObjectID","INSTALL_NUM","POINT_X","POINT_Y","PHASEDESIGNATION","FeederID","Utility","eTransformerBank_GLOBALID","RegionName"]]


#%%
#df = df.astype({'INSTALL_NUM':str}, copy=True)
df2 = df.astype(str, copy=True)
df2.INSTALL_NUM


#%%
df.drop_duplicates(subset='INSTALL_NUM', keep='first', inplace=True)


#%%
df.groupby('INSTALL_NUM').filter(lambda x: len(x) > 1)


#%%
df.groupby(['INSTALL_NUM']).size().reset_index(name='count')


#%%
df.drop(['Utility'], axis=1, inplace=True)


#%%
df.tail()


#%%
df.to_csv(custAcctFile,header=False, index=True)

#%% [markdown]
# [```gis.features.SpatialDataFrame()```](https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.features.toc.html?highlight=spatialdataframe#arcgis.features.SpatialDataFrame.from_xy)

#%%
from arcgis.features import SpatialDataFrame
from arcgis.gis import GIS
from getpass import getpass
from IPython.display import display


#%%
sdf = SpatialDataFrame.from_xy(df,"POINT_X","POINT_Y")
gis = GIS(arcpy.GetActivePortalURL(), username=input("Enter User Name "), password=(getpass()))
#gis = GIS()
#portalDesc = arcpy.GetPortalDescription()
# search and list all items owned by connected user
#query=f'owner:{portalDesc["user"]["username"]} AND title:CW BaseMap'
#itemType="Feature Layer"
#sortField="title"
#sortOrder="asc"
# default max__items is 10
#maxItems=100
#m = gis.content.search(query,itemType,sortField,sortOrder,maxItems)


#%%
consumptionLyr = gis.content.import_data(sdf)


#%%
m = gis.map('Gainesville,FL')


#%%
m


#%%
m.add_layer(sdf,options={"renderer":"ClassedSizeRenderer","field_name":"MAXCONSUMPTION"})


#%%
m.add_layer(consumptionLyr,options={"renderer":"ClassedSizeRenderer","field_name":"MAXCONSUMPTION"})


#%%
m


