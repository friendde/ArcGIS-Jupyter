
# coding: utf-8

# GOAL:
# 
# - Create points using JSON URL from Open Data site
# - Publish the points to ArcGIS Online or ArcGIS Portal

# Inspired by:
# 
# - [Bryan McIntosh - Export ArcGIS Server Map Service Layer to Shapefile](http://www.spatialtimes.com/2016/03/extract-map-service-layer-shapefile-using-python/)
# - [Corey Schafer python JSON YouTube video](https://youtu.be/9N6a-VLBa2I)
# - [Corey Schafer GitHub](https://github.com/CoreyMSchafer/code_snippets/blob/master/Python-JSON/api.py)

# In[1]:


import urllib3
import json
import arcpy
import pandas as pd
import numpy as np


# [urllib3 SSL Warnings](https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings)

# In[ ]:


urllib3.disable_warnings()


# In[3]:


jsonURL = "https://data.cityofgainesville.org/resource/c2ek-5hm9.json"
#jsonURL = 'https://data.cityofgainesville.org/api/views/f4t5-t3b5/rows.json'
#geojsonURL = 'https://data.cityofgainesville.org/resource/pqg3-m2ek.geojson'
gdb = r"C:\Users\friendde\Documents\ArcGIS\Projects\MIMS\MIMS.gdb"
#fc = r"C:\Users\friendde\Documents\ArcGIS\Projects\MIMS\MIMS.gdb\ActiveBusiness\ActiveBusinessCity"
tbl = r"C:\Users\friendde\Documents\ArcGIS\Projects\MIMS\MIMS.gdb\BusinessCity"
#flds = ['BusinessName','BusinessPhone','BusinessType','BusinessAddress','BusinessOwner','POINT_X','POINT_Y','SHAPE@XY']
flds = ['BusinessName','BusinessPhone','BusinessType','BusinessAddress','BusinessOwner','POINT_X','POINT_Y']
location = [0,0]
tupleXY = (0,0)


# In[4]:


arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True
#arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)


# In[5]:


def getCoords(_dict):
    if _dict is None:
        return [0,0]
    else:
        #print(_dict.get('coordinates'))
        return _dict.get('coordinates')


# In[6]:


http = urllib3.PoolManager()
response = http.request('GET', jsonURL)
#response.status
#response.data


# In[7]:


data = json.loads(response.data)


# In[ ]:


#print(json.dumps(data, indent=2))


# In[ ]:


arcpy.TruncateTable_management(tbl)


# In[ ]:


# use try/except to catch keyerror
for item in data:
    try:
        cursor = arcpy.da.InsertCursor(tbl,flds)
        bizowner = item['owner']
        bizname = item['name']
        bizphone = item['business_phone']
        biztype = item['business_type']
        bizaddress = item['location_address']
        location = getCoords(item['location'])
        locationX = location[0]
        locationY = location[1]
        tupleXY = (locationX,locationY)
        #print(bizname,'\n','\t',bizphone,'\n','\t',biztype,'\n','\t',bizaddress,'\n','\t',locationX,locationY)
        #business = [bizname,bizphone,biztype,bizaddress,bizowner,locationX,locationY,tupleXY]
        business = [bizname,bizphone,biztype,bizaddress,bizowner,locationX,locationY]
        print(business)
        cursor.insertRow(business)
        del cursor
    except KeyError:
        location = [0,0]
        tupleXY = (0,0)
        continue


# ### Use numpy and pandas to export to CSV
#  
# Use arcpy [```TableToNumPyArray()```](http://pro.arcgis.com/en/pro-app/arcpy/data-access/tabletonumpyarray.htm)
# See also [Working with numpy in ArcGIS](http://pro.arcgis.com/en/pro-app/arcpy/get-started/working-with-numpy-in-arcgis.htm)
# 

# #nparr = arcpy.da.TableToNumPyArray(tbl,flds,skip_nulls=True)
# #pdarr = pd.DataFrame(nparr)
# #pdarr.to_csv(custAcctFile,header=False, index=False)

# Ready new numpy array for consumption analysis

# In[8]:


nparr = arcpy.da.TableToNumPyArray(tbl,flds,skip_nulls=True)
df = pd.DataFrame(nparr)
df.head(10)


# In[ ]:


df.groupby('BusinessType')['BusinessType'].value_counts()


# #pivot table
# pivotTbl = df.pivot_table(values=["BusinessType"], index=["BusinessType"], aggfunc='count')
# pivotTbl

# [```gis.features.SpatialDataFrame()```](https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.features.toc.html?highlight=spatialdataframe#arcgis.features.SpatialDataFrame.from_xy)

# In[9]:


from arcgis.features import SpatialDataFrame
from arcgis.gis import GIS
from getpass import getpass
from IPython.display import display


# In[23]:


sdf = SpatialDataFrame.from_xy(df,"POINT_X","POINT_Y")
display(sdf)


# In[24]:


#gis = GIS("https://wms.gru.com/portal", username=input("Enter User Name "), password=(getpass()))
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


# In[25]:


bizLayer = gis.content.import_data(sdf)


# In[19]:


m = gis.map('Gainesville,FL')


# In[20]:


m


# In[27]:


m.add_layer(bizLayer)
m

