import os, sys
import hashlib
import requests
import base64
import json
import zipfile
import pathlib
from datetime import datetime, timezone
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper
###################  EDIT VALUES BELOW AS NEEDED  #################################
#
# POLARIS PLATFORM 
#
api_token = os.environ['POLARIS_API_TOKEN']
api_url =  os.environ['POLARIS_API_URL']
appname = os.environ['POLARIS_APP_NAME']
projectname = os.environ['POLARIS_PROJECT_NAME']
entitlementIds = [os.environ['POLARIS_SCA_ENTITLEMENT'], os.environ['POLARIS_SAST_ENTITLEMENT']]
sast_entitlementId = os.environ['POLARIS_SAST_ENTITLEMENT']
scantypes = ["SAST","SCA"]
testnotes = ""
triage = "NOT_ENTITLED"
###################  ^^^^^ EDIT VALUES ABOVE ^^^^ #################################
fileName = "polarispackage.zip"
dt = datetime.now(timezone.utc)
tz_dt = dt.astimezone()
iso_date = tz_dt.isoformat()
#
# GET FILE SIZE
#
filestats = os.stat(fileName)
fileSize = filestats.st_size
#
# GETTING HASH VALUE OF FILE
#
def get_md5(fileName):
    hasher = hashlib.md5()
    with open(fileName, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return base64.b64encode(hasher.digest()).decode('utf-8')
fileHash=get_md5(fileName)
#
# API CALLS
#
# ENDPOINTS
uploadurl = api_url + "test-manager/tests/artifacts"
testurl = api_url + "test-manager/tests"
portfoliourl = api_url + "portfolio/portfolios"

# GET PORTFOLIO INFO
headers = {
"accept": "application/vnd.synopsys.pm.portfolio-1+json",
"Api-Token": api_token
}
portfolioresponse = requests.get(portfoliourl, headers=headers)

# IF SUCCESSFUL
if portfolioresponse.status_code == 200:
	
	# SET PORTFOLIO ID
	portfolioId = portfolioresponse.json()['_items'][0]['id']
	
	# GET CATALOG INFO
	catalogurl = api_url + "portfolio/portfolios/" + portfolioId + "/catalog?_filter=name%3D%3D" + appname + "&_limit=1"
	catalogheaders = {
	"accept": "application/vnd.synopsys.pm.portfolio-catalog-1+json",
	"Api-Token": api_token
	}	
	catalogresponse = requests.get(catalogurl, headers=catalogheaders)

	# FIND APPLICATION AND PROJECT IDs
	applicationId = catalogresponse.json()['_items'][0]['id']
	
	# UPDATE PROJECT ITEMS API ENDPOINT
	projectitemsurl = api_url + "portfolio/portfolio-items/" + applicationId + "/portfolio-sub-items/?name=" + projectname + "&_limit=1"
	
	# GET PROJECT ITEM INFO
	projectitemheaders = {
	"accept": "application/vnd.synopsys.pm.portfolio-subitems-1+json",
	"Api-Token": api_token
	}	
	projectitemresponse = requests.get(projectitemsurl, headers=projectitemheaders)

	projectId = projectitemresponse.json()['_items'][0]['id']
	portfolioItemId = projectitemresponse.json()['_items'][0]['portfolioItemId']
	portfolioSubItemId = projectitemresponse.json()['_items'][0]['id']
	branchId = projectitemresponse.json()['_items'][0]['defaultBranch']['id']
	
	# PRINT PROJECT IDS
	print("###################################")
	print('Portfolio ID: ', portfolioId)
	print('Application ID: ', applicationId)
	print('Project ID: ', projectId)
	print('Branch ID: ', branchId)
	print("###################################")
	
	# UPLOAD FILE TO POLARIS
	headers = {
	"accept": "application/vnd.synopsys.tm.test-artifacts-1+json",
	"Content-Type": "application/vnd.synopsys.tm.test-artifacts-1+json",
	"Accept-Language": "en-CA,en;q=0.9",
	"Api-Token": api_token
	}

	data = {
	"fileName": fileName,
	"fileHash": fileHash,
	"fileSize": fileSize,
	"entitlementId": sast_entitlementId,
	"artifactType": "SOURCE_CODE",
	"createdAt": iso_date
	}
	uploadresponse = requests.post(uploadurl, headers=headers, json=data)
	if uploadresponse.status_code == 200:
		aid = uploadresponse.json()['artifactId']
		signedurl = uploadresponse.json()['signedUrl']
		data = {
		"applicationId": applicationId,
		"projectId": projectId,
		"entitlementIds": entitlementIds,
		"artifacts": [
		aid
		],
		"notes": testnotes,
		"portfolioItemId": portfolioItemId,
		"portfolioSubItemId": portfolioSubItemId,
		"assessmentTypes": scantypes,
		"testMode": "SOURCE_UPLOAD",
		"branchId": branchId,
		"triage": triage
		}
		#print(data)
		headers= {
		"Content-Type": "application/vnd.synopsys.tm.tests-bulk-1+json",
		"Accept-Language": "en-CA,en;q=0.9",
		"Api-Token": api_token
		}
		#
		# START FILE UPLOAD
		#
		thefile = open(fileName, 'rb').read()
		uploadheaders = {
			"Content-Type":"application/binary",
		}
		file_path = os.path.abspath(fileName)

		with open(file_path, "rb") as f:
			with tqdm(total=fileSize, unit="B", unit_scale=True, unit_divisor=1024) as t:
				wrapped_file = CallbackIOWrapper(t.update, f, "read")
				upload = requests.put(signedurl,data=wrapped_file,headers=uploadheaders)
		if upload.status_code == 200:
			print("Upload Complete")
		else:
			print(response.json())
		#
		# START TEST
		#		
		testresponse = requests.post(testurl, headers=headers, json=data)
		if testresponse.status_code == 207:
			print("Running Test.")
		else:
			print(testresponse.json())
	else:
		print(uploadresponse.json())
else:
	print(portfolioresponse.json())
