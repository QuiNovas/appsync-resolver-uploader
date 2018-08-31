# app-resolver-uploader

####A command line tool for uploading AppSync resolvers into AWS AppSyncL

This is intended to be used in a CI/CD process for managing AppSync resolvers

###Usage
```
python -m appsync_resolver_uploader --aws-access-key-id accesskey --aws-secret-access-key secret --aws_region region --api-id id 
```

###Arguments
- **aws-access-key-id** The AWS Access Key ID for the IAM user
- **aws-secret-access-key** The AWS Secret Access Key for the IAM user
- **aws-region** The AWS Region of the AppSync API to update
- **api-id** The API ID of the AppSync API to upload the schema to
 