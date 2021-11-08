# Function that gets data from the Usage API

This function gets the summary usage for a tenancy from the Usage API.

## Prerequisites

Before you deploy this sample function, make sure you have run step A, B and C of the [Oracle Functions Quick Start Guide for Cloud Shell](https://www.oracle.com/webfolder/technetwork/tutorials/infographics/oci_functions_cloudshell_quickview/functions_quickview_top/functions_quickview/index.html)
* A - Set up your tenancy
* B - Create application
* C - Set up your Cloud Shell dev environment

## Setup

Necessary steps before deployment:

* Create VCN
* Create subnet
* Allow port 443 in the security list

## Create policies

- Create Dynamic Group for Oracle Functions

``ALL {resource.type = 'fnfunc', resource.compartment.id = 'ocid1.compartment.oc1..aaaaaaaawjeriye4hdpx5la3sz7rpvafezrrgdx2w6p6kumfpw44vppqwnjq'}``

- Allow API GW access to Oracle Functions

``ALLOW any-user to use functions-family in compartment <COMPARTMENT_NAME> where ALL {request.principal.type= 'ApiGateway', request.resource.compartment.id = '<COMPARTMENT_OCID>'}``

- Allow Oracle Functions Dynamic Group access to OCI resources

``Allow dynamicgroup fnfunc_appdev to manage all-resources in tenancy``

## Configure Oracle Functions and deploy the function

* Create an Auth token
* Create an API key
* Create a function application
* Set up the local environment

``fn create context usageapi --provider oracle``

``fn use context usageapi``

``fn update context <COMPARTMENT_ID>``

``fn update context api-url https://functions.eu-frankfurt-1.oraclecloud.com``

``docker login -u '<tenancy>/<user>' fra.ocir.io``

``fn deploy --app <APP_NAME>``

  * Call the function to test

``echo -n '{"tenantId": "<TENANCY_OCID>","granularity": "MONTHLY","timeUsageStarted": "2020-10-10T00:00:00.000Z","timeUsageEnded": "2021-10-10T00:00:00.000Z"}' | fn invoke <APP_NAME> usage``

  * Create an API Gateway
  * Create a deployment that invokes the function
  * [OPTIONAL] Create the OAuth2 configuration in IDCS and API GW to use JWT token authorization