# import modules you will need
import arcpy
import numpy
import pandas as pd
from arcgis.features import SpatialDataFrame
from arcgis.gis import GIS
from getpass import getpass

# define variables
gdb = r"C:\Users\friendde\Documents\ArcGIS\Projects\LightsInstallNum\LightsInstallNum.gdb"
lightSource = r"C:\GISData\Data\Snapshot\mxElectric.geodatabase\Electric\main.eLight"
lightDest = r"C:\Users\friendde\Documents\ArcGIS\Projects\LightsInstallNum\LightsInstallNum.gdb\eLight"
lightFields = ["GLOBALID","FACILITYID","INSTALL_NUM","STREETADDRESS","STRUCTUREID","SHAPE@"]
lightFieldsNumPy = ["GLOBALID","FACILITYID","INSTALL_NUM","STREETADDRESS","STRUCTUREID"]
lightCSVFile = r'C:\Users\friendde\Documents\ArcGIS\Projects\LightsInstallNum\lights.csv'

# define workspace explicitly
arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True

# clean up your workspace and copy down new data if necessary, because over write output does not seem to work
if arcpy.Exists(lightDest):
    print(f'Found {lightDest}')
    arcpy.TruncateTable_management(lightDest)

# set up editing
edit = arcpy.da.Editor(gdb)
edit.startEditing(False, False)
edit.startOperation()

# perform your search cursor and insert results in to truncated light feature class
with arcpy.da.SearchCursor(lightSource,lightFields,"INSTALL_NUM NOT LIKE '5000%'") as lights:
    for light in lights: 
        print(light)
        with arcpy.da.InsertCursor(lightDest,lightFields)as ic:
            ic.insertRow(light)
  
# stop editing and save edits
edit.stopOperation()
edit.stopEditing(True)

# Use numpy and pandas to export to CSV if necessary.
# 
# Use arcpy TableToNumPyArray() http://pro.arcgis.com/en/pro-app/arcpy/data-access/tabletonumpyarray.htm
# See also Working with numpy in ArcGIS http://pro.arcgis.com/en/pro-app/arcpy/get-started/working-with-numpy-in-arcgis.htm
# Geometry is not supported so use altered field list

nparr = arcpy.da.FeatureClassToNumPyArray(lightDest,lightFieldsNumPy,skip_nulls=True)
df = pd.DataFrame(nparr)
# us head() to list rows, top five is default
df.head()
# export to CSV if necessary
df.to_csv(lightCSVFile,header=True, index=False)

# convert pandas data frame object to Spatial data Frame object
# https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.features.toc.html?highlight=spatialdataframe#arcgis.features.SpatialDataFrame.from_xy
sdf = SpatialDataFrame.from_featureclass(lightDest)
# sign into ArcGIS Online aka portal
gis = GIS(arcpy.GetActivePortalURL(), username=input("Enter User Name "), password=(getpass()))

# import the data into AtcGIS Online
lightLayer = gis.content.import_data(sdf)

# the following sets up a map object for display in Jupyter, then adds the layer to map and draws map in Jupyter
m = gis.map('Gainesville,FL')
m.add_layer(lightLayer)
m