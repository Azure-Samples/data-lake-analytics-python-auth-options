## AADTokenCredentials for multi-factor authentication
from msrestazure.azure_active_directory import AADTokenCredentials

## Required for Azure Data Lake Analytics job management
from azure.mgmt.datalake.analytics.job import DataLakeAnalyticsJobManagementClient
from azure.mgmt.datalake.analytics.job.models import JobInformation, JobState, USqlJobProperties

## Other required imports
import adal, uuid, time

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

def authenticate_username_password():
    """
    Authenticate using user w/ username + password.
    This doesn't work for users or tenants that have multi-factor authentication required.
    """
    authority_host_uri = 'https://login.microsoftonline.com'
    tenant = '<TENANT>'
    authority_uri = authority_host_uri + '/' + tenant
    resource_uri = 'https://management.core.windows.net/'
    username = '<USERNAME>'
    password = '<PASSWORD>'
    client_id = '<CLIENT_ID>'

    context = adal.AuthenticationContext(authority_uri, api_version=None)
    mgmt_token = context.acquire_token_with_username_password(resource_uri, username, password, client_id)
    credentials = AADTokenCredentials(mgmt_token, client_id)

    return credentials

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

if __name__ == '__main__':
    creds = authenticate_device_code()

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
