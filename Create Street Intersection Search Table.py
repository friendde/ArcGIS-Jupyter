
# coding: utf-8

# In[1]:


import arcpy
import numpy as np
import pandas as pd

sourceStreets = r'C:\GISData\Data\Snapshot\mxBaseMap.geodatabase\main.Cartographic\main.Streets'
destGDB = r'C:\Users\friendde\Documents\ArcGIS\Projects\NAStreets\NAStreets.gdb'
stIntersection = r'C:\Users\friendde\Documents\ArcGIS\Projects\NAStreets\NAStreets.gdb\StreetIntersection'
stVertices = r'C:\Users\friendde\Documents\ArcGIS\Projects\NAStreets\NAStreets.gdb\StreetVertices'
identEnds = r'C:\Users\friendde\Documents\ArcGIS\Projects\NAStreets\NAStreets.gdb\IdenticalStreetEnds'
fldNames = {'IntersectingStreets':'Intersecting Streets','StreetName1':'Street Name 1','StreetName2':'Street Name 2','StreetName3':'Street Name 3','StreetName4':'Street Name 4'}


# In[8]:
arcpy.env.workspace = destGDB
for fc in arcpy.ListFeatureClasses():
    arcpy.Delete_management(fc)
for tbl in arcpy.ListTables():
    arcpy.Delete_management(tbl)

sr = arcpy.Describe(sourceStreets).spatialReference
arcpy.CreateFeatureclass_management(destGDB,'StreetIntersection','POINT',spatial_reference=sr,out_alias='Steet Intersection')
for fName,fAlias in fldNames.items():
    #print(fName,fAlias)
    arcpy.AddField_management (stIntersection,fName,'TEXT',field_length=100,field_alias=fAlias,)


# In[9]:


arcpy.FeatureVerticesToPoints_management(sourceStreets,stVertices,'BOTH_ENDS')
arcpy.FindIdentical_management(stVertices,identEnds,'SHAPE',output_record_option='ONLY_DUPLICATES')


# In[10]:


lastFeatSeq = [row for row in arcpy.da.SearchCursor(identEnds, "FEAT_SEQ")][-1]
lastFeatSeq = lastFeatSeq[0]+1
print(f"number of intersections: {lastFeatSeq}")


# In[14]:

# TODO create list from column Feat_Seq instead of range()
arr = arcpy.da.TableToNumpyArray(identEnds,'FEAT_SEQ')
df = pd.DataFrame(arr)
df.head()
dfList = df['FEAT_SEQ'].tolist()
#for i in range(1,lastFeatSeq,1):
for featSeq in dfList
    FID = []
    streetIntersection = []
    with arcpy.da.SearchCursor(identEnds,["IN_FID","FEAT_SEQ"],f"FEAT_SEQ = {featSeq}") as sc:
        for fid in sc:
            FID.append(fid[0])
        for oid in FID:
            with arcpy.da.SearchCursor(stVertices,["OID@","Street_Label","SHAPE@"],f'OBJECTID = {oid}') as stCur:
                for st in stCur:
                    streetIntersection.append(st[1])
        # Convert list to set and then back to list to remove duplicate street label names
        streetIntersect.sort() = list(set(streetIntersection))
        print(f"sorted list {streetIntersect} length {len(streetIntersect)}")
        # convert list to string
        stringIntersect = ' '.join(streetIntersect)
        print(f"string list {stringIntersect}")
        ic = arcpy.da.InsertCursor(stIntersection,["IntersectingStreets","SHAPE@"])
        row = [stringIntersect,st[2]]
        ic.insertRow(row)
        del ic