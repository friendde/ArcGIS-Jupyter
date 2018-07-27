
import arcpy
import os, sys
from arcgis.gis import GIS
from arcgis import features
from getpass import getpass #to accept passwords in an interactive fashion
from getpass import getuser
from IPython.display import display

# Set the default path to ArcGIS Pro projects
prjPath = (os.environ['USERPROFILE']+'\Documents\ArcGIS\Projects\\')
#print(prjPath)

changePath = input(f'Default ArcGIS Project Path is: {prjPath}, change path? [Y or N]')
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

response = input(f'Do you want to use the active portal - {(arcpy.GetActivePortalURL())} [Y or N]')
if response.upper() in "YES":
    portal = arcpy.GetActivePortalURL()
else:
    portal = input("Enter portal address")

display(portal)
#portal = 'https://www.arcgis.com' # Can also reference a local portal
user = input("enter username")
#print(getuser())
password = getpass()
gis = GIS(portal, user, password)
print(f'Connected to {portal}')

# https://esri.github.io/arcgis-python-api/apidoc/html/arcgis.gis.toc.html#arcgis.gis.GroupManager
# https://developers.arcgis.com/python/guide/accessing-and-managing-groups/
# list groups and group id
for grp in gis.groups.search():
    print(grp.title, grp.groupid)

# search and list all items owned by connected user
query="owner:{}".format(user)
item_type="Feature Layer"
sort_field="title"
sort_order="asc"
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

# Local paths to create temporary content
sddraft = os.path.join(prjPath, "{}.sddraft".format(sdItem.title))
print(sddraft)
sd = os.path.join(prjPath, "{}.sd".format(sdItem.title))
print(sd)

arcpy.env.overwriteOutput = True
prjMap = arcpy.mp.ArcGISProject(aprx)
#m = prjMap.listMaps()[0]
prjMaps = prjMap.listMaps()
for prjMap in prjMaps:
    #useMap = input(f'Use map {} [Y/N]'(prjMap))
    if useMap.upper(input(f'Use map {} [Y/N]'(prjMap))) in 'Y':
        m = prjMap
        break

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

sdItem.share(everyone=False, org=True, groups="Energy Delivery Engineering", allow_members_to_edit=False)

