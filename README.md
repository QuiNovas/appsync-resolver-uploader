# app-resolver-uploader

#### A command line tool for uploading AppSync resolvers into AWS AppSyncL

This is intended to be used in a CI/CD process for managing AppSync resolvers

### Usage
```
python -m appsync_resolver_uploader --aws-access-key-id accesskey --aws-secret-access-key secret --aws_region region --api-id id --type-name type --field-name field --datasource-name datasource --request-mapping-template request.vtl --response-mapping-template response.vtl 
```

### Arguments
- **aws-access-key-id** The AWS Access Key ID for the IAM user
- **aws-secret-access-key** The AWS Secret Access Key for the IAM user
- **aws-region** The AWS Region of the AppSync API to update
- **api-id** The API ID of the AppSync API to upload the schema to
- **type-name** The name of the GraphQL Type
- **field-name** The name of the GraphQL field to attach the resolver to
- **datasource-name** The name of the AppSync data source for which the resolver is being created
- **request-mapping-template** The request mapping VTL file to upload
- **response-mapping-template** The response mapping VTL file to upload
