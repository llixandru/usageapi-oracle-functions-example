# Configure Usage API with Oracle Functions and API Gateway

This is a guide explaining how to connect to the Usage API through a secure REST API, leveraging [Oracle Functions](https://docs.oracle.com/en-us/iaas/Content/Functions/home.htm), [API Gateway](https://docs.oracle.com/en-us/iaas/Content/APIGateway/home.htm) and [Identity Cloud Service](https://docs.oracle.com/en/cloud/paas/identity-cloud/).

## 1. Description

The Usage API, like all APIs at your disposal on OCI, requires the REST calls to be signed respecting the [HTTP Signatures IETF standard](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures-08).

In order to learn more about how the signature is constructed programmatically, please refer to the [official documentation](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/signingrequests.htm#Request_Signatures).

### Flow Diagram

![Description of the flow and interconnection between services](https://i.postimg.cc/QCtKpMJk/Untitled-Diagram2-drawio.png)

The client (application, cURL request, Postman etc) makes a REST call to the Identity and Access Management Provider (IDCS) in order to obtain a JWT Token. This token is used to authenticate the following REST call to the Usage API.

API Gateway provides a link between the client URL and the backend function written in Python. API Gateway will check the validity of the JWT Token through the standard [OAuth2](https://oauth.net/2/) flow, and once the request is authenticated, will call the specific function.

The function in Oracle Functions authenticates to OCI as a resource principal and makes the call to Usage API, passing through the JSON body of the request received from the client call.

The response is returned in JSON format.

## 2. Prerequisites

1. Dynamic Group and Policies

- Create Dynamic Group for Oracle Functions

	```
	ALL {resource.type = 'fnfunc', resource.compartment.id = '<COMPARTMENT_OCID>'}
	```

- Allow API GW access to Oracle Functions

	```
	ALLOW any-user to use functions-family in compartment <COMPARTMENT_NAME> where ALL {request.principal.type= 'ApiGateway', request.resource.compartment.id = '<COMPARTMENT_OCID>'}
	```

- Allow Oracle Functions Dynamic Group access to OCI resources

	```
	Allow dynamicgroup <DYN_GRP_NAME> to manage all-resources in tenancy
	```

2. Create a VCN and a subnet, and add port 433 to the security list in the Ingress Rules.

3. Obtain an Auth Token for your user, in order to be able to deploy the Oracle Functions function to OCI.

> NOTE: Before you can push and pull Docker images to and from  Oracle Cloud Infrastructure Registry  (also known as Container Registry), you must already have an auth token.

To create a new auth token:

1.  In the top-right corner of the  Console, open the  **Profile**  menu (![User menu icon](https://docs.oracle.com/en-us/iaas/Content/Resources/Images/usermenu.png))  and then click  **User Settings**  to view the details.
2.  On the  **Auth Tokens**  page, click  **Generate Token**.
3.  Enter a friendly description for the auth token.  Avoid entering confidential information.
4.  Click  **Generate Token**. The new auth token is displayed.
5.  Copy the auth token immediately to a secure location from where you can retrieve it later, because you won't see the auth token again in the  Console.
6.  Close the Generate Token dialog.

## 3. Set up Oracle Functions

### Create your first application

1.  Sign in to the  Console  as a functions developer.
2.  In the  Console,  open the  navigation menu  and click  **Developer Services**. Under  **Functions**, click  **Applications**.
3.  Select the region you are using with  Oracle Functions.
4.  Click  **Create Application**.

    [![This image shows the New Applicatoin dialog, with empty Name, VCN, and Subnets fields.](https://docs.oracle.com/en-us/iaas/Content/Functions/non-dita/quickstart-cloudshell/faas-new-application-1.png "Click to expand")](https://docs.oracle.com/en-us/iaas/Content/Functions/non-dita/quickstart-cloudshell/faas-new-application-1.png)
    
6.  Specify:
    -   ``usageapi`` as the name for the new application. You'll deploy your first function in this application, and specify this application when invoking the function.
    -   The VCN and subnet in which to run the function.
7.  Click  **Create**.

See  [detailed instructions](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionscreatingapps.htm#Creating_Applications)  for more information.

### Set up your local environment

#### Install and start Docker

In a terminal window in your development environment:
1.  Confirm that Docker is installed by entering:
-   ```
    docker version
    ```
 
    If you see an error message indicating that Docker is not installed, you have to install Docker before proceeding. See the  [Docker documentation](https://docs.docker.com/)  for your platform (for Oracle Linux, see  [here](https://docs.oracle.com/cd/E52668_01/E87205/html/docker_install_upgrade.html)).
    
    Assuming Docker is installed, go to the  [Prerequisites section of the Fn Project home page on GitHub](https://github.com/fnproject/fn#pre-requisites)  and confirm that the installed version of Docker is at least the minimum version specified there. If not, re-install Docker before proceeding.
    
-   Launch the standard hello-world Docker image as a container to confirm that Docker is running by entering:
    

1.  ```
    docker run hello-world
    ```

    
    If you see an error message indicating that Docker is not running, you have to start the Docker daemon before proceeding. See the  [Docker documentation](https://docs.docker.com/).
    

See  [Configuration Notes](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsstartdocker.htm#Start_Docker)  for more information.

#### Set up API signing key and OCI profile

1.  Sign in to the  Console  as a functions developer.
2.  Open the  **Profile**  menu (![User menu icon](https://docs.oracle.com/en-us/iaas/Content/Resources/Images/usermenu.png))  and click  **User Settings**.
3.  Under  **Resources**, click  **API Keys**, and then click  **Add API Key**.
4.  Select  **Generate API Key Pair**  in the  **Add API Key**  dialog.
    
    [![This image shows the Add API Key dialog, with the Generate API Key Pair option selected.](https://docs.oracle.com/en-us/iaas/Content/Functions/non-dita/quickstart-local/faas-add-API-key-1.png "Click to expand")](https://docs.oracle.com/en-us/iaas/Content/Functions/non-dita/quickstart-local/faas-add-API-key-1.png)
    
5.  Click  **Download Private Key**  and save the private key file (as a .pem file) in the  `~/.oci`  directory. (If the  `~/.oci`directory doesn't already exist, create it now).
6.  Click  **Add**  to add the new API signing key to your user settings.
    
    The  **Configuration File Preview**  dialog is displayed, containing a configuration file snippet with basic authentication information for a profile named  `DEFAULT`  (including the fingerprint of the API signing key you just created).
    
    [![This image shows the Configuration File Preview dialog, with basic authentication information for a profile named Default.](https://docs.oracle.com/en-us/iaas/Content/Functions/non-dita/quickstart-local/faas-config-file-preview-1.png "Click to expand")](https://docs.oracle.com/en-us/iaas/Content/Functions/non-dita/quickstart-local/faas-config-file-preview-1.png)
    
7.  Copy the configuration file snippet shown in the text box, and close the  **Configuration File Preview**  dialog.
8.  In a text editor, open the  `~/.oci/config`  file and paste the snippet into the file. (If the  `~/.oci/config`  file doesn't already exist, create it now).
9.  In the text editor, change the profile in the snippet you've just pasted, as follows:
    -   Change the name of the profile from  `[DEFAULT]`  to a name of your choosing (for example,  `[functions-developer-profile]`). Note that the  `~/.oci/config`  file cannot contain two profiles with the same name.
    -   Change the value of the  `key_file`  parameter of the profile to specify the path of the private key file (the .pem file) you downloaded earlier.
10.  In the text editor, save the changes you've made to the  `~/.oci/config`  file, and close the text editor.
11.  In a terminal window, change permissions on the private key file (the .pem file) to ensure that only you can read it, by entering:
    

1.  ```
    chmod go-rwx ~/.oci/<private-key-file-name>.pem
    ```
    

See Configuration Notes for more information about  [setting up an API signing key](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionssetupapikey.htm#Set_up_an_Oracle_Cloud_Infrastructure_API_Signing_Key_for_Use_with_Oracle_Functions)  and  [creating a profile](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsconfigureocicli.htm#Create_a_Profile_in_the_Oracle_Cloud_Infrastructure_CLI_Configuration_File).

#### Install Fn Project CLI

In a terminal window in your development environment:

1.  Install the Fn Project CLI using the appropriate instructions below for your environment:
    -   Linux or MacOS: Enter:
        

-   ```
    curl -LSs https://raw.githubusercontent.com/fnproject/cli/master/install | sh
    ```
    
-   MacOS using Homebrew: Enter:
    
-    ```
     brew update && brew install fn
        ```
        
    -   Windows: Follow the  [Install Fn Client instructions on GitHub](https://github.com/fnproject/docs/blob/master/fn/develop/running-fn-client-windows.md#install-fn-client).
    -   Linux, MacOS, or Windows: Download and run the binary from the  [Fn Project Releases page on GitHub](https://github.com/fnproject/cli/releases).
-   Confirm that the  Fn Project  CLI has been installed by entering:
    

1.  ```
    fn version
    ```
    

See  [Configuration Notes](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsinstallfncli.htm#Install_the_Fn_Project_CLI)  for more information.

#### Set up Fn Project CLI context provider --oracle

In a terminal window in your development environment:

1.  Create a new  Fn Project  CLI context by entering:
    

-   ```
    fn create context <my-context> --provider oracle
    ```
    
    Note that you specify  `--provider oracle`  to enable authentication and authorization using  Oracle Cloud Infrastructurerequest signing, private keys, user groups, and policies that grant permissions to those user groups.
    
-   Specify that the  Fn Project  CLI is to use the new context by entering:
    
-   ```
    fn use context <my-context>
    ```
    
-   Configure the new  Fn Project  CLI context with the name of the OCI profile you've created for use with  Oracle Functions  (for example,  `[functions-developer-profile]`), by entering:
    

1.  ```
    fn update context oracle.profile <profile-name>
    ```
    

See  [Configuration Notes](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionscreatefncontext.htm#Create_an_Fn_Project_CLI_Context_to_Connect_to_Oracle_Cloud_Infrastructure)  for more information.

[5. Complete Fn Project CLI context configuration](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsquickstartlocalhost.htm#)

In a terminal window in your development environment:

1.  Configure the new  Fn Project  CLI context with the OCID of the compartment you want to own deployed functions
    

-   ```
    fn update context oracle.compartment-id <compartment-ocid>
    ```
    
-   Configure the new context with the api-url endpoint to use when calling the OCI API by entering:
    
	```
	fn update context api-url https://functions.eu-amsterdam-1.oraclecloud.com
	```

2.  Configure the  Fn Project  CLI context with the  Oracle Cloud Infrastructure Registry  address in the current region and tenancy that you want to use with  Oracle Functions:
    
    ```
    fn update context registry ams.ocir.io/axtbilobwx4h/[OCIR-REPO]
    ```
3. Log into the Registry using the Auth Token as your password

	 ```
	 docker login -u 'axtbilobwx4h/user@email.com' ams.ocir.io
	 ```

See  [Configuration Notes](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionscreatefncontext.htm#Create_an_Fn_Project_CLI_Context_to_Connect_to_Oracle_Cloud_Infrastructure)  for more information.

#### Deploy the function

1. In a terminal window, change to the directory where your function code is stored.

	```
	cd usage
	```

2. Deploy the function to Oracle Functions.

	```
	fn deploy --app usageapi
	```

## 4. Set up API Gateway

### Create your API gateway

1.  Sign in to the  Console  as an  API Gateway  developer,  open the  navigation menu  and click  **Developer Services**. Under  **API Management**, click  **Gateways**.
2.  Click  **Create Gateway**  and specify:
    
    -   a name for the new gateway, such as  `usage-api-gw`
    -   the type of the new gateway as  **Public**
    -   the name of the compartment in which to create  API Gateway  resources
    -   the name of the VCN to use with  API Gateway
    -   the name of the public regional subnet in the VCN
    
    [![This image shows the Create Gateway dialog, with all fields empty by default, except for the Type field which is set to Public by default.](https://docs.oracle.com/en-us/iaas/Content/APIGateway/non-dita/quickstart-apigateway/apigw-create-gateway-1.png "Click to expand")](https://docs.oracle.com/en-us/iaas/Content/APIGateway/non-dita/quickstart-apigateway/apigw-create-gateway-1.png)
    
3.  Click  **Create**.
    
    When the new API gateway has been created, it is shown as  **Active**  in the list on the  **Gateways**  page.
    

See  [detailed instructions](https://docs.oracle.com/en-us/iaas/Content/APIGateway/Tasks/apigatewaycreatinggateway.htm#Creating_an_API_Gateway)  for more information.

### Create your  API deployment

1.  On the  **Gateways**  page in the  Console, click the name of the API gateway you created earlier.
2.  Under  **Resources**, click  **Deployments**, and then click  **Create Deployment**.
3.  Click  **From Scratch**  and in the  **Basic Information**  section, specify:
    
    -   a name for the new API deployment, such as  `usageapi`
    -   a path prefix to add to the path of every route contained in the API deployment, such as  `/usage`
    -   the compartment in which to create the new API deployment
    
    [![This image shows the Basic Information page of the Create Deployment workflow, with the From Scratch option selected. Other fields are empty by default.](https://docs.oracle.com/en-us/iaas/Content/APIGateway/non-dita/quickstart-apigateway/apigw-create-deployment-basic-info-1.png "Click to expand")](https://docs.oracle.com/en-us/iaas/Content/APIGateway/non-dita/quickstart-apigateway/apigw-create-deployment-basic-info-1.png)
    
4.  Click  **Next**  and in the  **Route 1**  section, specify:
    
    -   a path,  `/request-summarized-usages`
    -   a method accepted by the back-end service,  `POST`
    -   the type of the back-end service, and associated details:
		    - Oracle Functions
		    - Choose the function called ``usage`` from the drop down list.
    
    [![This image shows the Routes page of the Create Deployment workflow, with all fields empty by default.](https://docs.oracle.com/en-us/iaas/Content/APIGateway/non-dita/quickstart-apigateway/apigw-create-deployment-route1-1.png "Click to expand")](https://docs.oracle.com/en-us/iaas/Content/APIGateway/non-dita/quickstart-apigateway/apigw-create-deployment-route1-1.png)
    
5.  Click  **Next**  to review the details you entered for the new API deployment, and click  **Create**  to create it.
    
    When the new API deployment has been created, it is shown as  **Active**  in the list of API deployments.
    
See  [detailed instructions](https://docs.oracle.com/en-us/iaas/Content/APIGateway/Tasks/apigatewaycreatingdeployment.htm#consolescratch)  for more information.

## 5. Set up OAuth2 in IDCS

### Prerequisites for using JWTs

When enabling authentication and authorization using JWTs, you must consider the following:

-   You have to use an identity provider (Auth0, Oracle IDCS, etc) that can issue JWTs for users. In our example we will focus on IDCS.
-   You can set up custom claims in authorization policies in your identity provider
-   Remote vs Static keys
    -   In API Gateway, you’ll have a choice between using Remote JWKS (JSON Web Key Set) or Static Key in the authentication policy for the validation of JWTs:
        -   **Remote JWKS**  will be retrieving the public verification keys from the identity provider at runtime
        -   **Static Keys** will be using public verification keys already issued by an identity provider and API Gateway will be able to verify JWTs locally without having to contact the identity provider

In this example, we’ll be using  **Static Keys** and **IDCS** as an identity provider.

### Obtain JWKS Static Key from IDCS

_Permission required: IDCS Administrator rights_

Before creating the Authentication Policy in API Gateway, we should obtain the JWKS Static Key from our Identity Provider – IDCS.

1. From the IDCS Console – You can connect to it via OCI from the **Identity & Security** Menu -> **Federation** -> **OracleIdentityCloudService** and now click on the  _Oracle Identity Cloud Service Console_ link:

![IDCS console URL](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-console.png)

2. In IDCS, go to **Settings** -> **Default Settings** and **Toggle ON** the **Access Signing Certificate** option and save:

![enter image description here](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-signin-certificate.png)

3. Get the JWKS from IDCS

Replace  **<YOUR-IDCS-URL>**  with your tenancy IDCS domain path which should look like this:  

```
https://idcs-1234xxx.identity.oraclecloud.com/admin/v1/SigningCert/jwk
```

When accessing the URL above, you’ll get a JSON file with the key as a response – save the response somewhere as we’ll need it later.

> Once you’ve retrieved the JWKS Key, go back to IDCS and  **Toggle OFF**  the Access Signing Certificate option to prevent unauthorized access.

### Create the Authentication Policy

#### Edit the existing API Deployment

Edit the deployment created earlier.

![](https://mytechretreat.com/wp-content/uploads/2021/05/edit-deployment.png)

#### Add an Authentication Policy

In the API Request Policies section from the Deployment – Click the **Add** button next to **Authentication:**

![](https://mytechretreat.com/wp-content/uploads/2021/05/add-auth.png)

#### Configure Authentication Policy

Configure the policy as follows:

![](https://mytechretreat.com/wp-content/uploads/2021/05/configure-auth-1-1.png)

- Authentication Type: JWT
- Authentication Token: Header
- Authentication Scheme: Bearer
- Issuers: https://identity.oraclecloud.com/
- Audiences: Specify a value that is allowed in the audience (aud) claim of a JWT to identify the intended recipient of the token. For this example, we’ll be setting the audience with the API gateway’s hostname

![](https://mytechretreat.com/wp-content/uploads/2021/05/configure-auth-2.png)

- Type: Static Keys
- KEY ID: SIGNING_KEY
- Format: JSON Web Key

Example: 

```
{ “kid”: “SIGNING_KEY”, “kty”: “RSA”, “use”: “sig”, “alg”: “RS256”, “n”: “abc123xxx”, “e”: “AQAB” }
```

All the values for these parameters you’ll find them in the JWKS saved from IDCS. Replace the values with the ones from your IDCS key

_For more info on what each field represents – please check  [the documentation.](https://docs.oracle.com/en-us/iaas/Content/APIGateway/Tasks/apigatewayusingjwttokens.htm)_

**Apply** the changes and click on  **Next**.



### Create IDCS applications to generate and validate JWTs

We need to create two confidential applications in IDCS to generate and then to validate the tokens:

-   Resource Server – this application will be used to validate the tokens
-   Client Application – this application will be used by a consumer to obtain the tokens

The relationship between the Resource Server and Client Application can be 1:many. As a best practice, we would create separate client applications for each consumer.

#### Create the Resource Server Application

The Resource Server Application will be used for JWT validation.

1. From the IDCS dashboard – go to  **Applications**  and click on **Add** and select **Confidential Application**

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-resource-app.png)

2. Give the Resource Server application a  **Name** and click on **Next**

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-resource-app-2.png)

3. **Skip the Client configuration**  as this will be our Resource Server Application

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-resource-app-3.png)

4. Configure this application as a resource server

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-resource-app-44.png)

5. Set the  **Primary Audience**  with the same value as set in the deployment’s authentication settings. In this case, we’ve set it to be our API Gateway hostname.

6. Add a  **scope**  for OAuth. For this example, it can be whatever you want – we’ll just use it for token generation.

7. We’ll go into more details on how to use the scopes for access segregation in a following article. For now, let’s just create one scope to use for all requests.

8. Click on **Next**.

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-resource-app-5.png)

9. **Skip** the Web Tier Policy – click on **Next** and then on **Finish**

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-resource-app-6.png)

10. Once finished, **Activate** the application.

#### Create the Client Application

The Client Application will be used by the API consumers to obtain JWTs.

To reiterate – as a best practice, we would create separate client applications for each API consumer.

1. From the IDCS dashboard – go to  **Applications**  and click on **Add** and select **Confidential Application**

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-resource-app.png)

1. Give the Client Application a  **Name** and click on **Next**

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-client-app-1.png)

3. **Configure this application as a client** and check **Client Credentials** and **JWT Assertion**

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-client-app-2.png)

4. Add the  **scopes**  defined in our Resource Server app

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-client-app-3-1.png)

5. Select the **Resource Server** application created before

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-client-app-4.png)

6. Select the **scope** and click **Add**

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-client-app-555.png)

7. The scope should now be added with the format:  **<primary-audience>/<scope-name>**

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-client-app-66.png)

8. Click on **Next** and skip the rest of the screens

> A Client ID and Client Secret for this client application will be generated for you at the end of the process.

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-client-app-7.png)

9. You should note these down – but you’ll be able to get them later as well, from the **Configuration** tab.

![](https://mytechretreat.com/wp-content/uploads/2021/05/idcs-create-client-app-8.png)

10. **Activate** the application.

## 6. Test the service

Using cURL, Postman or any other REST client, test out the services:

1. Get the JWT Token form IDCS:
```
curl --location --request POST 'https://idcs-1234xxxx.identity.oraclecloud.com/oauth2/v1/token' \
--header 'Authorization: Basic <BASE64 ENCODED CLIENT_ID:CLIENT_SECRET>' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'grant_type=client_credentials' \
--data-urlencode 'scope=<scope>'
```
2. Call the API Gateway endpoint:
```
curl --location --request POST 'https://1234xxxx.apigateway.<region>.oci.customer-oci.com/usage/request-summarized-usages' \
--header 'Authorization: Bearer <TOKEN>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "tenantId": "<TENANT_OCID>",
    "granularity": "MONTHLY",
    "timeUsageStarted": "2020-10-10T00:00:00.000Z",
    "timeUsageEnded": "2021-10-10T00:00:00.000Z"
}'
```


> Written with [StackEdit](https://stackedit.io/) by Liana Lixandru.
> Guide for setting up Oauth2 with IDCS for API Gateway available here: https://mytechretreat.com/complete-guide-how-to-configure-oauth-2-0-with-jwt-idcs-on-oci-api-gateway/