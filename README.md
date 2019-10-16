---
languages:
- python
products:
- azure
- azure-active-directory
page_type: sample
description: "When building an application with Python SDK for Data Lake Analytics, you need to pick how your application will sign in to Azure Active Directory."
---

# Authenticating your Python application against Azure Active Directory

## Overview

When building an application that uses the Python SDK for Data Lake Analytics (ADLA), you need to pick how your application will sign in to Azure Active Directory (AAD). 

There are two fundamental ways to have your application sign-in:
* **Interactive** - Use this method when your application has a user directly using your application and your app needs to perform operations in the context of that user.
* **Non-interactive** - Thus this method when your application is not meant to interact with ADLA as a specific user. This is useful for long-running services.

## Required Python packages

* [adal](https://pypi.python.org/pypi/adal/0.4.7) - v0.4.7
* [azure-mgmt-datalake-analytics](https://pypi.python.org/pypi/azure-mgmt-datalake-analytics/0.2.0) - v0.2.0


If you have Python installed, you can install these packages via the command line with the following commands:

```
pip install adal==0.4.7
pip install azure-mgmt-datalake-analytics==0.2.0
```

## Required imports

To simplify the code samples, ensure you have the following `import` statements at the top of your code.

```python
## AADTokenCredentials for multi-factor authentication
from msrestazure.azure_active_directory import AADTokenCredentials

## Required for Azure Data Lake Analytics job management
from azure.mgmt.datalake.analytics.job import DataLakeAnalyticsJobManagementClient
from azure.mgmt.datalake.analytics.job.models import JobInformation, JobState, USqlJobProperties

## Other required imports
import adal, uuid, time
```

## Basic authentication workflow

For a given domain (tenant). Your code needs to get credentials (tokens) for each end Azure REST endpoint (token audience) that you intend to use. Once the credentials are retrieved, then REST clients are built using those credentials.

#### Token Audiences
These are the Azure REST endpoints (token audiences) that are used in the samples:
* Azure Resource Manager management operations: ``https://management.core.windows.net/``. 
* Azure Data Lake data plane operations: ``https://datalake.azure.net/``.

#### Domains and Tenant

You can retrieve your AAD domain / tenant ID by going to the [Azure portal](https://portal.azure.com/) and clicking 'Azure Active Directory'. An example domain is "contoso.onmicrosoft.com".

#### Client ID

All clients must have a "Client ID" that is known by the domain you are connecting to.

#### Sample code

```python
if __name__ == '__main__':
    creds = authenticate_device_code()
```

The `authenticate_*TYPE*` represents one of three different helper methods used in the samples. The helper methods are shown below.

## Interactive login

There are two ways to use interactive login:
* **Interactive Pop-up** - The device the user is using will see a prompt appear and will use that prompt. This document does not cover this case yet.
* **Interactive Device code** - The device the user is using will NOT see a prompt. This is useful in those cases when, for example, it is not possible to show a prompt. 

### Authenticate interactively with a device code

This option is used when you want to have a browser popup appear when the user signs in to your application, showing an AAD login form. From this interactive popup, your application will receive the tokens necessary to use the Data Lake Analytics Python SDK on behalf of the user.

This is not supported yet.

### Authenticate interactively with a device code

Azure Active Directory also supports a form of authentication called "device code" authentication. Using this, you can direct your end-user to a browser window, where they will complete their sign-in process before returning to your application.

```python
def authenticate_device_code():
    """
    Authenticate the end-user using device auth.
    """
    authority_host_uri = 'https://login.microsoftonline.com'
    tenant = '<TENANT_ID_OR_DOMAIN>'
    authority_uri = authority_host_uri + '/' + tenant
    resource_uri = 'https://management.core.windows.net/'
    client_id = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'

    context = adal.AuthenticationContext(authority_uri, api_version=None)
    code = context.acquire_user_code(resource_uri, client_id)
    print(code['message'])
    mgmt_token = context.acquire_token_with_device_code(resource_uri, code, client_id)
    credentials = AADTokenCredentials(mgmt_token, client_id)

    return credentials
```

> NOTE: The client id used above is a well known that already exists for all azure services. While it makes the sample code easy to use, for production code you should use generate your own client ids for your application.

### Non-interactive - Service principal - Authentication

Use this option if you want to have your application authenticate against AAD using its own credentials, rather than those of a user. Using this process, your application will receive the tokens necessary to use the Data Lake Analytics Python SDK as a service principal, 
which represents your application in AAD.

Non-interactive - Service principal / application
 * Using a secret key
 * Using a certificate

#### Service principals
To create service principal [follow the steps in this article](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-authenticate-service-principal).

#### Authenticate non-interactively with a secret key

```python
def authenticate_client_key():
    """
    Authenticate using service principal w/ key.
    """
    authority_host_uri = 'https://login.microsoftonline.com'
    tenant = '<TENANT>'
    authority_uri = authority_host_uri + '/' + tenant
    resource_uri = 'https://management.core.windows.net/'
    client_id = '<CLIENT_ID>'
    client_secret = '<CLIENT_SECRET>'

    context = adal.AuthenticationContext(authority_uri, api_version=None)
    mgmt_token = context.acquire_token_with_client_credentials(resource_uri, client_id, client_secret)
    credentials = AADTokenCredentials(mgmt_token, client_id)

    return credentials
```

#### Authenticate non-interactively with a certificate

```python
def authenticate_client_cert():
    """
    Authenticate using service principal w/ cert.
    """
    authority_host_uri = 'https://login.microsoftonline.com'
    tenant = '<TENANT>'
    authority_uri = authority_host_uri + '/' + tenant
    resource_uri = 'https://management.core.windows.net/'
    client_id = '<CLIENT_ID>'
    client_cert = '<CLIENT_CERT>'
    client_cert_thumbprint = '<CLIENT_CERT_THUMBPRINT>'

    context = adal.AuthenticationContext(authority_uri, api_version=None)

    mgmt_token = context.acquire_token_with_client_certificate(resource_uri, client_id, client_cert, client_cert_thumbprint)
    credentials = AADTokenCredentials(mgmt_token, client_id)

    return credentials
```

#### Setting up and using Data Lake SDKs
Once your have followed one of the approaches for authentication, you're ready to set up your ADLA Python SDK client objects, which you'll use to perform various actions with the service. Remember to use the right tokens/credentials with the right clients: use the ADL credentials for data plane operations, and use the ARM credentials for resource- and account-related operations.

You can then perform actions using the clients, like so:

```python
    adla_account = '<ADLA_ACCOUNT_NAME>'
    resource_group = '<RESOURCE_GROUP_NAME>'
    sub_id = '<SUBSCRIPTION-ID>'

    job_client = DataLakeAnalyticsJobManagementClient(creds, 'azuredatalakeanalytics.net')

    script = '@a = SELECT * FROM (VALUES ("Hello, World!")) AS T(message); OUTPUT @a TO "/Samples/Output/HelloWorld.csv" USING Outputters.Csv();'

    job_id = str(uuid.uuid4())

    job_client.job.create(adla_account, job_id, JobInformation(
        name='HelloWorld',
        type='USql',
        properties=USqlJobProperties(script=script)
    ))

    job_result = job_client.job.get(adla_account, job_id)

    while job_result.state != JobState.ended:
        print('Job is not yet done. Waiting for 3 seconds. Current state: ' + job_result.state.value)
        time.sleep(3)
        job_result = job_client.job.get(adla_account, job_id)    

    print('Job finished with result: ' + job_result.result.value)
```

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
