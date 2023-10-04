# NodeGoat - Polaris Upload and Scan

At times you simply need to package your app, and send and upload for it to be analyzed using the Synopsys Polaris Platform. This workflow is possible via the UI, however doing this in the CI would require tools, a local install, and build of your app. This script will simply take a number of inputs, package your application once built and upload it to be scanned by Polaris.

## Getting Started

There are essentially 4 steps necessary:

### Step 1:

Make sure the following secret environment variables are set:
- POLARIS_API_URL
- POLARIS_API_TOKEN
- POLARIS_APP_NAME
- POLARIS_PROJECT_NAME
- POLARIS_SCA_ENTITLEMENT
- POLARIS_SAST_ENTITLEMENT

### Step 2:

Make sure the requirements.txt file is placed in your working space root folder.

### Step 3:

Make sure the .polaris-uploadandscan.py file is placed in your working space root folder. 

### Step 4:

Add the action to build your project. Once built you will simply need to add the code to zip your workspace and execute the python script. Should look similar to this.

```
      - run: zip -9 -r --exclude=*.git*  polarispackage.zip ${GITHUB_WORKSPACE}
      - name: Run Polaris Scan
        shell: bash
        env:
          POLARIS_API_URL: ${{ secrets.POLARIS_API_URL }}
          POLARIS_API_TOKEN: ${{ secrets.POLARIS_ACCESS_TOKEN }}
          POLARIS_APP_NAME: ${{ secrets.POLARIS_APP_NAME }}
          POLARIS_PROJECT_NAME: ${{ secrets.POLARIS_PROJECT_NAME }}
          POLARIS_SCA_ENTITLEMENT: ${{ secrets.POLARIS_SCA_ENTITLEMENT }}
          POLARIS_SAST_ENTITLEMENT: ${{ secrets.POLARIS_SAST_ENTITLEMENT }}
        run: |
          pip3 install -r requirements.txt
          python3 .polaris-uploadandscan.py
          rm -rf polarispackage.zip
```

### Please note 
this was originally created to work in Jenkins. This concept can be replicated to most CI environment following the same simple steps and adjusting the environment variables being passed to the script.

### Credits
Many thanks to John O. and Sean H. Takes a village, and you guys are awesome.
