
# coding: utf-8

# In[1]:


import arcpy
import os, sys
from arcgis.gis import GIS
from arcgis import features
from getpass import getpass #to accept passwords in an interactive fashion
from getpass import getuser
from IPython.display import display


# In[2]:


# Set the default path to ArcGIS Pro projects
prjPath = (os.environ['USERPROFILE']+'\Documents\ArcGIS\Projects\\')
#print(prjPath)


# In[3]:


changePath = input(f'Default ArcGIS Project Path is: {}, change path? [Y or N]'(prjPath))
if changePath.upper() in "YES":
    prjPath = input('Enter new path '')
    os.chdir(prjPath)
for project in os.listdir(prjPath):
    usePrj = input(f'Use project {} [Y or N]'(project))
    if usePrj.upper() in "YES":
        prjPath = os.path.join(prjPath,project)
        break
for root, dirs, files in os.walk(prjPath):
    for file in files:
        if file.endswith(".aprx"):
            aprx = os.path.join(root, file)
            display(aprx)


# In[4]:


response = input(f'Do you want to use the active portal - {} [Y or N]'(arcpy.GetActivePortalURL()))
if response.upper() in "YES":
    portal = arcpy.GetActivePortalURL()
else:
    portal = input("Enter portal address")

display(portal)
#portal = 'https://www.arcgis.com' # Can also reference a local portal
user = input("enter username")
#print(getuser())
password = getpass()
print(f'Connecting to {}'(portal))
gis = GIS(portal, user, password)


# In[5]:


# search and list all items owned by connected user
query="owner:{}".format(user)
item_type="Feature Layer"
sort_field="title"
sort_order="asc"
max_items=100
search_result = gis.content.search(query,item_type,sort_field,sort_order,max_items)
for i in range(len(search_result)):
    display(search_result[i])
    updateResult = input(f'Update {} [Y,N]'(search_result[i].title))
    if updateResult.upper() in "YES":
        sd_fs_name = search_result[i].title
        print(sd_fs_name)
        query = "owner:{} AND title:{}".format(user,sd_fs_name)
        sdItem = gis.content.search(query,item_type="Service Definition")[0]
        print(sdItem)
        break


# In[6]:


# Local paths to create temporary content
#relPath = sys.path[0]
sddraft = os.path.join(prjPath, "{}.sddraft".format(sdItem.title))
print(sddraft)
sd = os.path.join(prjPath, "{}.sd".format(sdItem.title))
print(sd)


# In[7]:


arcpy.env.overwriteOutput = True
prjMap = arcpy.mp.ArcGISProject(aprx)
#m = prjMap.listMaps()[0]
prjMaps = prjMap.listMaps()
for prjMap in prjMaps:
    #useMap = input(f'Use map {} [Y/N]'(prjMap))
    if useMap.upper(input(f'Use map {} [Y/N]'(prjMap))) in 'Y':
        m = prjMap
        break


# In[8]:


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
#sd_filename = service + ".sd"
#sd_output_filename = os.path.join(outdir, sd)
arcpy.StageService_server(sddraft, sd)

# Share to portal
print("Uploading Service Definition...")
arcpy.UploadServiceDefinition_server(sd, "My Hosted Services")

print("Uploaded service.")


# In[ ]:


sdItem.share(everyone=False, org=True, groups="Energy Delivery Engineering", allow_members_to_edit=False)

