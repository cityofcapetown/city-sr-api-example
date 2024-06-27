import argparse
import csv
import logging
import pathlib
import sys
import re

import coct_sr_api_client
from coct_sr_api_client.api import auth_group_api, config_group_api

logger = logging.getLogger(__name__)


def validate_hex_string(value: str) -> str:
    if not re.match(r'^[0-9a-fA-F]{32}$', value.replace("-", "")):
        raise argparse.ArgumentTypeError('Invalid hex string: must be 32 characters long')
    return value


def validate_csv(value: str) -> pathlib.Path:
    value = pathlib.Path(value)

    if not str(value).lower().endswith('.csv'):
        raise argparse.ArgumentTypeError("Only .csv files are supported")
    elif not value.parent.exists():
        raise argparse.ArgumentTypeError(f"Directory '{value.parent}' does not exist")

    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-p', '--public-key', type=validate_hex_string, required=True,
                        help='Public key (32 character long UUID)')
    parser.add_argument('-k', '--private-key', type=validate_hex_string, required=True,
                        help='Private key (32 character long UUID)')
    parser.add_argument('-o', '--output-file', type=validate_csv, required=True,
                        help='Path to output CSV file')
    parser.add_argument('-v', '--verbose', action='store_true', required=False,
                        help="Turn on verbose logging")

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s: %(message)s')

    logger.debug(f'Received arguments: {args.public_key=}, {args.output_file=}'
                 f'args.private_key="{"*" * len(args.private_key)}"')

    configuration = coct_sr_api_client.Configuration(
        host="https://qaeservices1.capetown.gov.za/coct/api"
    )
    # Setting the service Identifier
    configuration.api_key['serviceAuth'] = args.public_key.replace("-", "")

    with coct_sr_api_client.ApiClient(configuration) as api_client:
        auth_api_instance = auth_group_api.AuthGroupApi(api_client)
        logger.info("Logging into API")
        login_response = auth_api_instance.zcur_guest_login_get_without_preload_content(
            args.private_key.replace("-", "")
        )

        # Copying out the auth cookie, and setting it
        # clunkier than I expected
        set_cookie = login_response.headers['set-cookie']
        sap_sso_cookie, *_ = set_cookie.split(";")
        configuration.api_key['cookieAuth'] = sap_sso_cookie

        logger.info("Logged into API")

        logger.info("Starting an API session")
        # Setting the API session
        session_response = auth_api_instance.zsreq_session_get()
        configuration.api_key['sessionAuth'] = session_response.session_id

        # Setting up the config instance
        config_api_instance = config_group_api.ConfigGroupApi(api_client)

        # Fetching the typ information from the API
        sr_type_response = config_api_instance.zsreq_config_types_get()
        sr_subtype_response = config_api_instance.zsreq_config_subtypes_get()

        logger.info("Ending API session")

    logger.info("Writing out to file")
    type_records = tuple((
        (type_config.type, type_config.name, subtype_config.subtype, subtype_config.name)
        for type_config in sr_type_response
        for subtype_config in sr_subtype_response
        if subtype_config.type == type_config.type
    ))
    with open(args.output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(["type", "type_name", "subtype", "subtype_name"])
        for record in type_records:
            csv_writer.writerow(record)

    logger.info("Wrote out to file")
