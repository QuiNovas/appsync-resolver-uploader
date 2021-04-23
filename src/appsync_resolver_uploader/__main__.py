from __future__ import print_function

import argparse
import atexit
import boto3
import json
import logging
import sys

if sys.argv[0].endswith("__main__.py"):
    sys.argv[0] = "python -m appsync_resolver_uploader"


@atexit.register
def app_exit():
    logging.getLogger().info("Terminating")


def _parse_command_line_arguments():
    argv_parser = argparse.ArgumentParser()
    argv_parser.add_argument(
        '--aws-access-key-id',
        help='The AWS IAM Access Key ID to use'
    )
    argv_parser.add_argument(
        '--aws-secret-access-key',
        help='The AWS IAM Secret Access Key to use'
    )
    argv_parser.add_argument(
        '--aws-region',
        help='The AWS Region of the AppSync API to update'
    )
    argv_parser.add_argument(
        '--api-id',
        help='The API Id of the AppSync API to update'
    )
    argv_parser.add_argument(
        '--type-name',
        help='The name of the GraphQL Type'
    )
    argv_parser.add_argument(
        '--field-name',
        help='The name of the GraphQL field to attach the resolver to'
    )
    argv_parser.add_argument(
        '--datasource-name',
        help='The name of the AppSync data source for which the resolver is being created - not used for pipeline resolvers'
    )
    argv_parser.add_argument(
        '--request-mapping-template',
        help='The request mapping VTL file to upload - Optional if the datasource is a Lamba'
    )
    argv_parser.add_argument(
        '--response-mapping-template',
        help='The response mapping VTL file to upload - Optional if the datasource is a Lamba'
    )
    argv_parser.add_argument(
        '--pipeline-config',
        help='The list of functions to use in this resolver - format is name,dataSourceName;name,dataSourceName'
    )
    return argv_parser.parse_args()


def main():
    try:
        args = _parse_command_line_arguments()

        # set AWS logging level
        logging.getLogger('botocore').setLevel(logging.ERROR)
        logging.getLogger('boto3').setLevel(logging.ERROR)

        request_mapping_template = None
        response_mapping_template = None
        if args.request_mapping_template:
            with open(args.request_mapping_template) as vtl:
                request_mapping_template = vtl.read()
        if args.response_mapping_template:
            with open(args.response_mapping_template) as vtl:
                response_mapping_template = vtl.read()

        appsync = boto3.client(
            'appsync',
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key,
            region_name=args.aws_region
        )

        action = appsync.update_resolver
        print('Searching for existing resolver')
        try:
            appsync.get_resolver(
                apiId=args.api_id,
                typeName=args.type_name,
                fieldName=args.field_name
            )
        except appsync.exceptions.NotFoundException:
            print('Resolver does not exist, creating')
            action = appsync.create_resolver
        else:
            print('Found resolver, updating')
        kwargs = {
            'apiId': args.api_id,
            'typeName': args.type_name,
            'fieldName': args.field_name
        }
        if args.pipeline_config:
            function_ids = []
            for function in [x for x in args.pipeline_config.split(';') if x]:
                name, data_source_name = function.split(',')
                function_id = _find_function(appsync, args.api_id, name, data_source_name)
                if not function_id:
                    raise ValueError('Function name {}, datasource {} not found'.format(name, data_source_name))
                function_ids.append(function_id)
            if not (request_mapping_template and response_mapping_template):
                raise ValueError('request-mapping-template and response-mapping-template are required for a pipeline resolver')
            kwargs['requestMappingTemplate'] = request_mapping_template
            kwargs['responseMappingTemplate'] = response_mapping_template
            kwargs['kind'] = 'PIPELINE'
            kwargs['pipelineConfig'] = {
                'functions': function_ids
            }
        else:
            kwargs['dataSourceName'] = args.datasource_name
            kwargs['kind'] = 'UNIT'
            if request_mapping_template:
                kwargs['requestMappingTemplate'] = request_mapping_template
            if response_mapping_template:
                kwargs['responseMappingTemplate'] = response_mapping_template

        print('Resolver upload complete\n', json.dumps(action(**kwargs), indent=4, sort_keys=True))
    except KeyboardInterrupt:
        print('Service interrupted', file=sys.stderr)
    except Exception as e:
        print('Upload FAILED:', e.message, file=sys.stderr)
        print('')
        raise e


def _find_function(appsync, api_id, name, data_source_name, next_token=None):
    if next_token:
        response = appsync.list_functions(
            apiId=api_id,
            nextToken=next_token
        )
    else:
        response = appsync.list_functions(
            apiId=api_id
        )
    function_id = None
    if 'nextToken' in response:
        function_id = _find_function(appsync, api_id, name, data_source_name, response['nextToken'])
    for function in response['functions']:
        if function['name'] == name and function['dataSourceName'] == data_source_name:
            if function_id:
                raise ValueError('Function name {}, dataSourceName {} tuple is not unique, unable to determine function'.format(name, data_source_name))
            function_id = function['functionId']
    return function_id


if __name__ == '__main__':
    main()

