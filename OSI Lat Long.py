
# coding: utf-8

# # OSI Lat Long
# ### This Notebook uses the XY of the point featureclass and adds Lat Long to each related row in a related table
# A CSV file is generated that will be used to support a seperate project.
# 
# The second half of the Notebook explores the electric consumption data with a [SpatialDataFrame](https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.features.toc.html?highlight=spatialdataframe#spatialdataframe) using the customers table modifed in the first half.

# In[1]:


import arcpy
import numpy
import pandas as pd


# In[7]:


gdb = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb"

#esvcPntSource = r"C:\GISData\Data\Snapshot\mxElectric.geodatabase\Electric\main.eServicePoint"
#gsvcPntSource = r"C:\GISData\Data\Snapshot\mxGas.geodatabase\Gas\main.gMeterSet"
#rsvcPntSource = r"C:\GISData\Data\Snapshot\WWW_Extract.gdb\Reclaimed\rServicePoint"
#wsvcPntSource = r"C:\GISData\Data\Snapshot\WWW_Extract.gdb\Water\ServicePoint"
#svcPntSourceList = [esvcPntSource,gsvcPntSource,rsvcPntSource,wsvcPntSource]
#svcPntSourceList = [esvcPntSource]

esvcPntDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\eServicePoint"
gsvcPntDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\gMeterSet"
rsvcPntDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\rServicePoint"
wsvcPntDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\ServicePoint"
svcPntDestList = [esvcPntDest,gsvcPntDest,rsvcPntDest,wsvcPntDest]

#svcPntDict = {esvcPntSource:esvcPntDest,gsvcPntSource:gsvcPntDest,rsvcPntSource:rsvcPntDest,wsvcPntSource:wsvcPntDest}

ecustAcctSource = r"C:\GISData\Data\Snapshot\mxElectric.geodatabase\main.eCUSTOMERACCOUNT"
gcustAcctSource = r"C:\GISData\Data\Snapshot\mxGas.geodatabase\main.gCUSTOMERACCOUNT"
rcustAcctSource = r"C:\GISData\Data\Snapshot\WWW_Extract.gdb\rCustomerAccount"
wcustAcctSource = r"C:\GISData\Data\Snapshot\WWW_Extract.gdb\wCustomerAccount"
custAcctSourceList = [ecustAcctSource,gcustAcctSource,rcustAcctSource,wcustAcctSource]

ecustAcctDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\eCUSTOMERACCOUNT"
gcustAcctDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\gCUSTOMERACCOUNT"
rcustAcctDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\rCUSTOMERACCOUNT"
wcustAcctDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\wCUSTOMERACCOUNT"
custAcctDestList = [ecustAcctDest,gcustAcctDest,rcustAcctDest,wcustAcctDest]

custAcctDict = {ecustAcctSource:ecustAcctDest,gcustAcctSource:gcustAcctDest,rcustAcctSource:rcustAcctDest,wcustAcctSource:wcustAcctDest}

svcPntDestFlds = ["OID@","GLOBALID","POINT_X","POINT_Y","PHASEDESIGNATION"]
custAcctDestFlds = ["SERVICEPOINTOBJECTID","GLOBALID","POINT_X","POINT_Y","PHASEDESIGNATION","Utility"]
custAcctOutFlds = ["OID@","SvcPntOID","INSTALL_NUM","POINT_X","POINT_Y","PHASEDESIGNATION"]
custAnalysis = ["SERVICEPOINTOBJECTID","INSTALL_NUM","POINT_X","POINT_Y","AVGCONSUMPTION","MAXCONSUMPTION"]
custLocations = r"C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\OSILatLong.gdb\CustomerLocations"
custAcctFile = r'C:\Users\friendde\Documents\ArcGIS\Projects\OSILatLong\GISAll.csv'


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

# In[3]:


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

def listReplace(lst, _from, _to):
   return([_to if v == _from else v for v in lst])


# In[4]:


arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)


# In[5]:


fdsList = arcpy.ListDatasets()
for fds in fdsList:
    print(fds)
    arcpy.Delete_management(fds)
tblList = arcpy.ListTables()
for tbl in tblList:
    print(tbl)
    arcpy.Delete_management(tbl)
fcsList = arcpy.ListFeatureClasses()
for fcs in fcsList:
    print(fcs)
    arcpy.Delete_management(fcs)


# 
# for svcPntDest in svcPntDestList:
#     if arcpy.Exists(svcPntDest):
#         print(f'Found {svcPntDest}')
#         arcpy.Delete_management(svcPntDest)

# rc_list = [c.name for c in arcpy.Describe(workspace).children if c.datatype == "RelationshipClass"] 
# 
# FeatureClassToFeatureClass_conversion (in_features, out_path, out_name, {where_clause}, {field_mapping}, config_keyword)

# In[6]:


for k,v in custAcctDict.items():
    print(f'Copying {k} to {v}')
    arcpy.Copy_management(k,v)
    if arcpy.Exists(v):
        print(f'Copy Success {v}')
        arcpy.AddField_management(v, "POINT_X", "DOUBLE")
        arcpy.AddField_management(v, "POINT_Y", "DOUBLE")
        arcpy.AddField_management(v, "PHASEDESIGNATION", "LONG")
        arcpy.AddField_management(v, "SERVICEPOINTOBJECTID", "LONG")
        arcpy.AddField_management(v, "Utility", "TEXT")
    else:
        print(f'Copy Failed! {v}')
for fc in svcPntDestList:
    if arcpy.Exists(fc):
        print(f'Copy Success, adding XY to {fc}')
        arcpy.AddXY_management(fc)
        print(f'AddXY completed')
        fldList = []
        flds = arcpy.Describe(fc).fields
        for fld in flds:
            fldList.append(fld)
        if "PHASEDESIGNATION" not in fldList:
            print(f'Adding PhaseDesignation to {fc}')
            arcpy.AddField_management(fc, "PHASEDESIGNATION", "LONG")
            print(f'Add PhaseDesignation completed')


# In[7]:


rcList = [c.name for c in arcpy.Describe(gdb).children if c.datatype == "RelationshipClass"]
for rc in rcList:
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


# In[8]:


for rc in rcList:
    arcpy.MigrateRelationshipClass_management(rc)


# In[9]:


edit = arcpy.da.Editor(gdb)
edit.startEditing(False, False)
edit.startOperation()


# In[10]:


for rc in rcList:
    desc = arcpy.Describe(rc)
    if desc.originClassNames[0] == "SAP_INSTALLATION":
        pass
    elif desc.destinationClassNames[0] == "SAP_INSTALLATION":
        pass
    else:
        custAcctFlds = []
        custAcctFlds = listReplace(custAcctDestFlds,"GLOBALID",f"{desc.originClassNames[0]}_GLOBALID")
        with arcpy.da.SearchCursor(desc.originClassNames[0],svcPntDestFlds) as svcpnts:
            print(f"Searching {desc.originClassNames[0]} and updating {desc.destinationClassNames[0]}")
            for svcpnt in svcpnts:
                whereClause = f"{desc.originClassNames[0]}_GLOBALID = '{svcpnt[1]}'"
                with arcpy.da.UpdateCursor(desc.destinationClassNames[0],custAcctFlds,whereClause) as uc:
                    for row in uc:
                        row[0] = svcpnt[0]
                        row[2] = svcpnt[2]
                        row[3] = svcpnt[3]
                        row[4] = getPhaseDesignation(svcpnt[4])
                        row[5] = desc.destinationClassNames[0][:1]
                        uc.updateRow(row)


# In[11]:


edit.stopOperation()
edit.stopEditing(True)


# In[13]:


arcpy.CreateTable_management(gdb,custLocations,ecustAcctDest)
arcpy.Append_management (custAcctDestList,custLocations,"NO_TEST")


# ### Use numpy and pandas to export to CSV
# 
# Use arcpy [```TableToNumPyArray()```](http://pro.arcgis.com/en/pro-app/arcpy/data-access/tabletonumpyarray.htm)
# See also [Working with numpy in ArcGIS](http://pro.arcgis.com/en/pro-app/arcpy/get-started/working-with-numpy-in-arcgis.htm)

# In[8]:


nparr = arcpy.da.TableToNumPyArray(custLocations,custAcctOutFlds,skip_nulls=True)
#nparr = arcpy.da.TableToNumPyArray(custAcctDest,custAcctOutFlds,null_value=-9999)
pdarr = pd.DataFrame(nparr)
pdarr.to_csv(custAcctFile,header=False, index=False)


# TODO - write file to \\gruadmin.gru.com\fs\Groups\OMS Replacement Project\Documents for OSII\Customer and Premise Files

# Ready new numpy array for consumption analysis

# In[9]:


nparr = arcpy.da.TableToNumPyArray(custLocations,["SvcPntOID","POINT_X","POINT_Y","AVGCONSUMPTION","MAXCONSUMPTION","Utility"],skip_nulls=True)


# In[14]:


df = pd.DataFrame(nparr)
df.head(1000)


# [```gis.features.SpatialDataFrame()```](https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.features.toc.html?highlight=spatialdataframe#arcgis.features.SpatialDataFrame.from_xy)

# In[11]:


from arcgis.features import SpatialDataFrame
from arcgis.gis import GIS
from getpass import getpass
from IPython.display import display


# In[12]:


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


# In[13]:


consumptionLyr = gis.content.import_data(sdf)


# In[ ]:


m = gis.map('Gainesville,FL')


# In[ ]:


m.add_layer(sdf,options={"renderer":"ClassedSizeRenderer","field_name":"MAXCONSUMPTION"})


# In[ ]:


m.add_layer(consumptionLyr,options={"renderer":"ClassedSizeRenderer","field_name":"MAXCONSUMPTION"})


# In[ ]:


m

