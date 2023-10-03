# NodeGoat - Polaris Upload and Scan

At times you simply need to package your app, and send and upload for it to be analyzed using the Synopsys Polaris Platform. This workflow is possible via the UI, however doing this in the CI would require tools, a local install, and build of your app. This script will simply take a number of inputs, package your application once built and upload it to be scanned by Polaris.

## Getting Started

There are essentially 3 steps necessary:

### Step 1:

Make sure the following secret environment variables are set:
- POLARIS_API_URL
- POLARIS_API_TOKEN
- POLARIS_APP_NAME
- POLARIS_PROJECT_NAME
- POLARIS_SCA_ENTITLEMENT
- POLARIS_SAST_ENTITLEMENT

### Step 2:
