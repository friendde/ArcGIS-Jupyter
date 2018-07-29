
# coding: utf-8

# # Overwrite Portal Content with ArcGIS Pro Projects
# 
# This Notebook will use a [map](http://pro.arcgis.com/en/pro-app/help/mapping/map-authoring/maps.htm) in your [ArcGIS Pro Project](http://pro.arcgis.com/en/pro-app/get-started/overview-of-arcgis-pro.htm) to update [Items](http://doc.arcgis.com/en/arcgis-online/manage-data/add-items.htm) in your ArcGIS Online/Enterprise (collectivly called portal). If you want to [use a CSV file to update your Feature Layer](https://github.com/Esri/arcgis-python-api/blob/master/samples/05_content_publishers/overwriting_feature_layers.ipynb) in ArcGIS Online/Portal check out [Esri's GitHub Python API page](https://github.com/Esri/arcgis-python-api)
# 
# 

# #### Import Libraries
# 1. It all starts with the [arcgis.gis module](https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.gis.toc.html#module-arcgis.gis) which is the most important and provides the entry point into the GIS.
# 
# 2. The [getpass module](https://docs.python.org/3.7/library/getpass.html) provides two functions
#     * getpass() prompts for a password
#     * getuser() returns login name. This could be useful if your portal is federated with Active Directory
# 3. The [display](https://ipython.readthedocs.io/en/stable/api/generated/IPython.display.html?highlight=display#IPython.display.display) in IPython is similar to print() but does more in Jupyter

# In[ ]:


import os, sys
import arcpy
from arcgis.gis import GIS
from arcgis import features
from getpass import getpass
#from getpass import getuser
from IPython.display import display


# Now we get the input() from the user to set the ArcGIS Pro Project path then find the file extension of ArcGIS Pro Project to use later. 
# 
# The next cell uses Python 3 [formatted string literal](https://docs.python.org/3/reference/lexical_analysis.html#f-strings), or f-string. By the way [this is an excellent tutorial](https://realpython.com/python-f-strings/) on using f-strings
#     

# In[ ]:


prjPath = (os.environ['USERPROFILE']+'\Documents\ArcGIS\Projects\\')
changePath = input(f'Use default ArcGIS Project Path is: {prjPath}? [Y or N]')
if changePath.upper() in "YES":
    prjPath = input('Enter new path ')
    os.chdir(prjPath)
for project in os.listdir(prjPath):
    usePrj = input(f'Use project {project} [Y or N]')
    if usePrj.upper() in "YES":
        prjPath = os.path.join(prjPath,project)
        break
for root, dirs, files in os.walk(prjPath):
    for file in files:
        if file.endswith(".aprx"):
            aprx = os.path.join(root, file)
            display(aprx)


# Now we [get the active portal](http://pro.arcgis.com/en/pro-app/arcpy/functions/getactiveportalurl.htm) and instantiate the [GIS](https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.gis.toc.html#gis). The [GetPortalDescription()](http://pro.arcgis.com/en/pro-app/arcpy/functions/getportaldescription.htm) returns a dictionary containing portal information.

# In[ ]:


response = input(f'Do you want to use the active portal - {(arcpy.GetActivePortalURL())} [Y or N]')
if response.upper() in "YES":
    #arcpy.SignInToPortal(input("Enter portal address "), username=(input("Enter User Name ")), password=(getpass()))
    gis = GIS(arcpy.GetActivePortalURL(), username=input("Enter User Name "), password=(getpass()))
else:
    #arcpy.SignInToPortal(input("Enter portal address"), username=(input("Enter User Name")), password=(getpass()))
    gis = GIS(input("Enter portal address "), input("Enter User Name "), getpass())
portal_desc = arcpy.GetPortalDescription()
print(f'Connected to Organization {portal_desc["name"]}\nPortal Name {portal_desc["portalName"]} as user {portal_desc["user"]["username"]}')


# Using [gis.content.search()](https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.gis.toc.html#arcgis.gis.ContentManager.search) we are going to find all [item_types](https://developers.arcgis.com/rest/users-groups-and-items/items-and-item-types.htm) that are Feature Layers.

# https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.gis.toc.html#arcgis.gis.GroupManager
# https://developers.arcgis.com/python/guide/accessing-and-managing-groups/

# In[ ]:


# search and list all items owned by connected user
query=f'owner:{portal_desc["user"]["username"]}'
item_type="Feature Layer"
sort_field="title"
sort_order="asc"
# default max__items is 10
max_items=100
search_result = gis.content.search(query,item_type,sort_field,sort_order,max_items)
for i in range(len(search_result)):
    display(search_result[i])
    updateResult = input(f'Update {(search_result[i].title)} [Y,N]')
    if updateResult.upper() in "YES":
        sd_fs_name = search_result[i].title
        print(sd_fs_name)
        query = "owner:{} AND title:{}".format(user,sd_fs_name)
        sdItem = gis.content.search(query,item_type="Service Definition")[0]
        print(sdItem)
        break
if updateResult.upper() not in "YES":
    print(f'All Service Definitions in your Content on {portal} were presented')


# Name the ArcGIS Pro Project service definition draft and service definition the same as the service definition item selected above.

# In[ ]:


# Local paths to create temporary content
sddraft = os.path.join(prjPath, "{}.sddraft".format(sdItem.title))
#print(sddraft)
sd = os.path.join(prjPath, "{}.sd".format(sdItem.title))
#print(sd)


# In[ ]:


arcpy.env.overwriteOutput = True
prjMap = arcpy.mp.ArcGISProject(aprx)
#m = prjMap.listMaps()[0]
prjMaps = prjMap.listMaps()
for prjMap in prjMaps:
    if useMap.upper(input(f'Use map {prjMap} [Y/N]')) in 'YES':
        m = prjMap
        break


# In[ ]:


# Create FeatureSharingDraft and set service properties
sharing_draft = m.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", sdItem.title)
#sharing_draft.summary = "My Summary"
#sharing_draft.tags = "My Tags"
#sharing_draft.description = "My Description"
#sharing_draft.credits = "My Credits"
#sharing_draft.useLimitations = "My Use Limitations"
sharing_draft.overwriteExistingService = True

# Create Service Defintion Draft file
sharing_draft.exportToSDDraft(sddraft)

# Stage Service
arcpy.StageService_server(sddraft, sd)

# Share to portal
print("Uploading Service Definition...")
arcpy.UploadServiceDefinition_server(sd, "My Hosted Services")

print("Uploaded service.")


# https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.gis.toc.html#arcgis.gis.GroupManager.search

# In[ ]:


# search and list all groups owned by connected user
query=f'owner:{portal_desc["user"]["username"]}'
sort_field="title"
sort_order="asc"
max_groups=100
outside_org=False, 
categories=None
grps = []
for grp in gis.groups.search(querysort_field,sort_order,max_groups,outside_org,categories):
    print(grp.title, grp.groupid)
    #sdItem.share(everyone=False, org=True, groups="Energy Delivery Engineering", allow_members_to_edit=False)

