
# coding: utf-8

# ### This Notebook will use a formula to determine the reccomended KVA for a transformer when it is replaced
# The formula uses customer count and customer consumption history downsteam of each transformer. When Electric Trouble Crews replace a transformer the reccomended size will available when an Engineer is not (for example after hours or weekends). This will help ensure the right size transformer is used based on consumption history, and not merley just areplacement that could be under-sized or over-sized.
# The second half of the Notebook explores the electric consumption data with a [SpatialDataFrame](https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.features.toc.html?highlight=spatialdataframe#spatialdataframe) using the customers table modifed in the first half.
# 

# In[1]:


import arcpy
#import numpy
#import pandas as pd
from datetime import datetime


# In[2]:


gdb = r"C:\Users\friendde\Documents\ArcGIS\Projects\ReplaceKVA\ReplaceKVA.gdb"
txSource = r"C:\GISData\Data\Snapshot\mxElectric.geodatabase\Electric\main.eTransformerBank"
txDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\ReplaceKVA\ReplaceKVA.gdb\Electric\eTransformerBank"
svcPntDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\ReplaceKVA\ReplaceKVA.gdb\Electric\eServicePoint"
custAcctSource = r"C:\GISData\Data\Snapshot\mxElectric.geodatabase\main.eCUSTOMERACCOUNT"
custAcctDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\ReplaceKVA\ReplaceKVA.gdb\eCUSTOMERACCOUNT"
txAddFlds = ["kWDSum","CF","kWDSumXCF","kWDSumXCF_A","kWDSumXCF_B","kWDSumXCF_C"]
txUpdateFlds = ["GLOBALID","kWDSum","CF","kWDSumXCF","CUSTOMERCOUNT","MAXCUSTOMERCONSUMPTION_A","MAXCUSTOMERCONSUMPTION_B","MAXCUSTOMERCONSUMPTION_C","kWDSumXCF_A","kWDSumXCF_B","kWDSumXCF_C"]
txFlds = ["GLOBALID","kWDSum","CF","kWDSumXCF","CUSTOMERCOUNT","MAXCUSTOMERCONSUMPTION_A","MAXCUSTOMERCONSUMPTION_B","MAXCUSTOMERCONSUMPTION_C","DEVICEID","FEEDERID","FEEDERID2","INSTALLATIONDATE","PHASEDESIGNATION","SUBTYPE","RATEDKVA_A","RATEDKVA_B","RATEDKVA_C","STRUCTUREID","FACILITYID","AVGCUSTOMERCONSUMPTION_A","AVGCUSTOMERCONSUMPTION_B","AVGCUSTOMERCONSUMPTION_C","PURPOSE","STREETADDRESS","eSupportStructure_GlobalID","eSurfaceStructure_GlobalID"]
svcPntFlds = ["OID@","GLOBALID","eTransformerBank_GLOBALID","FEEDERID","PHASEDESIGNATION","SUBTYPE","CUSTOMERCOUNT","AVGCUSTOMERCONSUMPTION","MAXCUSTOMERCONSUMPTION","STREETADDRESS","eSupportStructure_GLOBALID"]
custAcctFlds = ["eServicePoint_GlobalID","MAXCONSUMPTION"]


# - For each customer downstream of a transformer, obtain Estimated Demand using summer or winter demand table, translate kwH (key) to kwD (vale). 
# - Sum the kwD 
# - Using coincidence factor dictionary, number of customers downstream of transformer (key) to obtain coincidence factor (value). - Multiply coincidence factor by sum of kwD
# - Result is minimum kvA transformer
#  
# Obtain CF using number of customers on transformer, convert maxconsumption to kwD 
# Multiply kwD by CF. Result is minimum kvA transformer.

# In[3]:


if datetime.today().month >= 5 <= 9:
    #print("Using Summer Peak")
    summerPeak = True
    estimatedDemand = {0:0,50:2.40,100:2.67,150:2.94,200:3.20,250:3.46,300:3.72,350:3.98,400:4.23,450:4.48,500:4.73,550:4.97,600:5.21,
                    650:5.45,700:5.68,750:5.92,800:6.15,850:6.37,900:6.60,950:6.82,1000:7.03,1050:7.25,1100:7.46,1150:7.67,
                    1200:7.88,1250:8.08,1300:8.28,1350:8.48,1400:8.67,1450:8.86,1500:9.05,1550:9.24,1600:9.42,1650:9.60,
                    1700:9.78,1750:9.95,1800:10.12,1850:10.29,1900:10.46,1950:10.62,2000:10.78,2050:10.94,2100:11.10,2150:11.26,
                    2200:11.41,2250:11.57,2300:11.73,2350:11.89,2400:12.05,2450:12.21,2500:2.36,2550:2.52,2600:12.68,2650:12.84,
                    2700:13.00,2750:13.16,2800:13.31,2850:13.47,2900:13.63,2950:13.79,3000:13.95}
else:
    #print("Using Winter Peak")
    winterPeak = True
    estimatedDemand = {0:0,50:1.97,100:2.33,150:2.69,200:3.05,250:3.41,300:3.76,350:4.11,400:4.45,450:4.80,500:5.14,550:5.48,
                       600:5.82,650:6.15,700:6.49,750:6.82,800:7.14,850:7.47,900:7.79,950:8.11,1000:8.43,1050:8.74,1100:9.05,
                       1150:9.36,1200:9.67,1250:9.97,1300:10.27,1350:10.57,1400:10.87,1450:11.16,1500:11.45,1550:11.74,1600:12.03,
                       1650:12.31,1700:12.60,1750:12.87,1800:13.15,1850:13.42,1900:13.70,1950:13.96,2000:14.23,2050:14.45,
                       2100:14.68,2150:14.90,2200:15.13,2250:15.35,2300:15.58,2350:15.80,2400:16.03,2450:16.25,2500:16.48,
                       2550:16.70,2600:16.93,2650:17.15,2700:17.38,2750:17.60,2800:17.83,2850:18.05,2900:18.28,2950:18.50,
                       3000:18.73}

# coincidence factor
cf = {0:0,1:1.0,2:0.85,3:0.74,4:0.66,5:0.61,6:0.57,7:0.54,8:0.52,9:0.5,10:0.49,11:0.47,12:0.46,13:0.45,14:0.43,15:0.42,16:0.41,
      17:0.39,18:0.38,19:0.38,20:0.37}


# In[4]:


arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True


# In[31]:


def sumSvcPnts(_GID):
    svcGUIDa = []
    svcGUIDb = []
    svcGUIDc = []
    svcGUIDab = []
    svcGUIDbc = []
    svcGUIDac = []
    svcGUIDabc = []
    consumptionA = []
    consumptionB = []
    consumptionC = []
    consumptionAB = []
    consumptionAC = []
    consumptionBC = []
    consumptionABC = []
    maxConA = 0
    maxConB = 0 
    maxConC = 0
    with arcpy.da.SearchCursor(svcPntDest,svcPntFlds,f"eTransformerBank_GLOBALID = '{_GID}'") as svcPnts:
        for svcPnt in svcPnts:
            print(f'svcPnt at eTransformerBank_GLOBALID = {svcPnt[2]}')
            # c phase
            if svcPnt[4] == 1:
                svcGUIDc.append(svcPnt[1])
            # b phase
            if svcPnt[4] == 2:
                svcGUIDb.append(svcPnt[1])
            # bc phase
            if svcPnt[4] == 3:
                svcGUIDbc.append(svcPnt[1])
            # a phase
            if svcPnt[4] == 4:
                svcGUIDa.append(svcPnt[1])
            # ac phase
            if svcPnt[4] == 5:
                svcGUIDac.append(svcPnt[1])
            # ab phase
            if svcPnt[4] == 6:
                svcGUIDab.append(svcPnt[1])
            # abc phase
            if svcPnt[4] == 7:
                svcGUIDabc.append(svcPnt[1])
    # a phase
    for guidA in svcGUIDa:
        consumptionA.append(getConsumption(guidA))
        maxConA = sum(consumptionA)
    # b phase
    for guidB in svcGUIDb:
        consumptionB.append(getConsumption(guidB))
        maxConB = sum(consumptionB)
    # c phase
    for guidC in svcGUIDc:
        consumptionC.append(getConsumption(guidC))
        maxConC = sum(consumptionC)
    # ab phase
    for guidAB in svcGUIDab:
        consumptionAB.append(getConsumption(guidAB))
        maxConA = maxConA + (sum(consumptionAB)/2)
        maxConB = maxConB + (sum(consumptionAB)/2)
    # ac phase
    for guidAC in svcGUIDac:
        consumptionAC.append(getConsumption(guidAC))
        maxConA = maxConA + (sum(consumptionAC)/2)
        maxConC = maxConC + (sum(consumptionAC)/2)
    # bc phase
    for guidBC in svcGUIDbc:
        consumptionBC.append(getConsumption(guidBC))
        maxConB = maxConB + (sum(consumptionBC)/2)
        maxConA = maxConC + (sum(consumptionBC)/2)
    # abc phase
    for guidABC in svcGUIDabc:
        consumptionABC.append(getConsumption(guidABC))
        maxConA = maxConA + (sum(consumptionABC)/3)
        maxConB = maxConB + (sum(consumptionABC)/3)
        maxConC = maxConC + (sum(consumptionABC)/3)
    print(maxConA,maxConB,maxConC)
    return maxConA,maxConB,maxConC

# In[27]:

def getConsumption(svcPntGUID):
    kwh = []  
    with arcpy.da.SearchCursor(custAcctDest,custAcctFlds,f"eServicePoint_GlobalID = '{svcPntGUID}'") as custAccts:
        for custAcct in custAccts:
            kwh.append(custAcct[1])
    return sum(kwh)

# In[7]:

# In[8]:

def getKWD(consumption): 
    for key in sorted(estimatedDemand.keys()):
        if consumption <= key:
            #print(key, estimatedDemand[key])
            return estimatedDemand[key]
    kwd = calcKWD(consumption)
    return kwd
def calcKWD(consumption):
    if summerPeak: 
        print(f'Using Summer Peak')
        sp = 13.9525*(consumption-3000)
        return sp 
    if winterPeak:
        print(f'Using Winter Peak')
        wp = 18.7027*(consumption-3000)
        return wp
def getCF(custCount):
    for key in sorted(cf.keys()):
        if custCount == key:
            #print(key, cf[key])
            return cf[key]
        if custCount >= 20:
            return .37


# In[10]:


tblList = arcpy.ListTables()
for tbl in tblList:
    print(tbl)
    arcpy.Delete_management(tbl)
fdsList = arcpy.ListDatasets()
for fds in fdsList:
    print(fds)
    arcpy.Delete_management(fds)


# In[11]:


arcpy.Copy_management(custAcctSource,custAcctDest)
for fld in txAddFlds:
    arcpy.AddField_management(txDest,fld,"DOUBLE")

# In[12]:


txMaxFlds = ["MAXCUSTOMERCONSUMPTION_A","MAXCUSTOMERCONSUMPTION_B","MAXCUSTOMERCONSUMPTION_C"]
for txMaxFld in txMaxFlds:
    arcpy.CalculateField_management(txDest,txMaxFld,0)
arcpy.CalculateField_management(svcPntDest,"MAXCUSTOMERCONSUMPTION",0)


# In[13]:


expression = "setZero(!MAXCONSUMPTION!)"
codeblock = """
def setZero(maxcon):
    if maxcon is None:
        return 0
    else:
        return maxcon"""
arcpy.CalculateField_management(custAcctDest,"MAXCONSUMPTION",expression,"PYTHON3",codeblock)


# In[12]:

edit = arcpy.da.Editor(gdb)
edit.startEditing(False, False)
edit.startOperation()

# In[32]:

# - For each customer downstream of a transformer, obtain Estimated Demand using summer or winter demand table, translate kwH (key) to kwD (vale). 
# - Sum the kwD 
# - Using coincidence factor dictionary, number of customers downstream of transformer (key) to obtain coincidence factor (value).
# - Multiply coincidence factor by sum of kwD
# - Result is minimum kvA transformer
with arcpy.da.UpdateCursor(txDest,txUpdateFlds) as txPnts:
    for txPnt in txPnts:
        if txPnt[4] is None:
            count = 0
        else:
            count = txPnt[4]
        kwh = [] 
        kwhSum = 0
        pha,phb,phc = sumSvcPnts(txPnt[0])
        print(pha,phb,phc)
        txPnt[5] = pha
        txPnt[6] = phb
        txPnt[7] = phc
        txPnt[8] = getKWD(pha) * getCF(count)
        txPnt[9] = getKWD(phb) * getCF(count)
        txPnt[10] = getKWD(phc) * getCF(count)
        txPnts.updateRow(txPnt)            

# In[ ]:

# In[ ]:

edit.stopOperation()
edit.stopEditing(True)


# ### Use numpy and pandas to export to CSV
# 
# Use arcpy [```TableToNumPyArray()```](http://pro.arcgis.com/en/pro-app/arcpy/data-access/tabletonumpyarray.htm)
# See also [Working with numpy in ArcGIS](http://pro.arcgis.com/en/pro-app/arcpy/get-started/working-with-numpy-in-arcgis.htm)

# nparr = arcpy.da.TableToNumPyArray(custAcctDest,custAcctOutFlds,skip_nulls=True)
# #nparr = arcpy.da.TableToNumPyArray(custAcctDest,custAcctOutFlds,null_value=-9999)
# pdarr = pd.DataFrame(nparr)
# pdarr.to_csv(custAcctFile,header=False, index=False)

# TODO - write file to \\gruadmin.gru.com\fs\Groups\OMS Replacement Project\Documents for OSII\Customer and Premise Files

# Ready new numpy array for consumption analysis

# nparr = arcpy.da.TableToNumPyArray(custAcctDest,["SERVICEPOINTOBJECTID","POINT_X","POINT_Y","AVGCONSUMPTION","MAXCONSUMPTION"],skip_nulls=True)

# df = pd.DataFrame(nparr)
# df.head()

# [```gis.features.SpatialDataFrame()```](https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.features.toc.html?highlight=spatialdataframe#arcgis.features.SpatialDataFrame.from_xy)

# from arcgis.features import SpatialDataFrame
# from arcgis.gis import GIS
# from getpass import getpass
# from IPython.display import display

# sdf = SpatialDataFrame.from_xy(df,"POINT_X","POINT_Y")
# gis = GIS(arcpy.GetActivePortalURL(), username=input("Enter User Name "), password=(getpass()))
# #gis = GIS()
# #portalDesc = arcpy.GetPortalDescription()
# # search and list all items owned by connected user
# #query=f'owner:{portalDesc["user"]["username"]} AND title:CW BaseMap'
# #itemType="Feature Layer"
# #sortField="title"
# #sortOrder="asc"
# # default max__items is 10
# #maxItems=100
# #m = gis.content.search(query,itemType,sortField,sortOrder,maxItems)

# #consumptionLyr = gis.content.import_data(sdf)

# m = gis.map('Gainesville,FL')

# m.add_layer(sdf,options={"renderer":"ClassedSizeRenderer","field_name":"MAXCONSUMPTION"})

# #m.add_layer(consumptionLyr,options={"renderer":"ClassedSizeRenderer","field_name":"MAXCONSUMPTION"})

# m

