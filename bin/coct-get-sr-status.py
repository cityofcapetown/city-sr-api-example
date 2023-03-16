import argparse
import logging
import pprint
import sys
import re

import coct_sr_api_client
from coct_sr_api_client.apis.tags import auth_group_api, config_group_api, service_request_group_api

logger = logging.getLogger(__name__)


def validate_reference_number(value):
    if not re.match(r'^9\d{9}$', value):
        raise argparse.ArgumentTypeError('Reference number must be a 10-digit number starting with 9')
    return value


def validate_hex_string(value):
    if not re.match(r'^[0-9a-fA-F]{32}$', value.replace("-", "")):
        raise argparse.ArgumentTypeError('Invalid hex string: must be 32 characters long')
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-r', '--reference-number', type=validate_reference_number, required=True,
                        help='Service request reference number to check')
    parser.add_argument('-p', '--public-key', type=validate_hex_string, required=True,
                        help='Public key (32 character long UUID)')
    parser.add_argument('-k', '--private-key', type=validate_hex_string, required=True,
                        help='Private key (32 character long UUID)')
    parser.add_argument('-v', '--verbose', action='store_true', required=False,
                        help="Turn on verbose logging")

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s: %(message)s')

    logger.debug(f'Received arguments: {args.reference_number=}, {args.public_key=}, '
                 f'args.private_key="{"*" * len(args.private_key)}"')

    configuration = coct_sr_api_client.Configuration(
        host="https://qaeservices1.capetown.gov.za/coct/api"
    )
    # Setting the service Identifier
    configuration.api_key['serviceAuth'] = args.public_key.replace("-", "")

    with coct_sr_api_client.ApiClient(configuration) as api_client:
        auth_api_instance = auth_group_api.AuthGroupApi(api_client)
        logger.info("Logging into API")
        login_response = auth_api_instance.zcur_guest_login_get({"cookie": args.private_key.replace("-", "")})

        # Copying out the auth cookie, and setting it
        # clunkier than I expected
        set_cookie = login_response.response.headers['set-cookie']
        sap_sso_cookie, *_ = set_cookie.split(";")
        configuration.api_key['cookieAuth'] = sap_sso_cookie

        logger.info("Logged into API")

        logger.info("Starting an API session")
        # Setting the API session
        session_response = auth_api_instance.zsreq_session_get()
        configuration.api_key['sessionAuth'] = session_response.body.session_id

        # Actually looking up the current state of the SR
        sr_api_instance = service_request_group_api.ServiceRequestGroupApi(api_client)
        sr_status_response = sr_api_instance.zsreq_sr_reference_no_get({"reference_no": str(args.reference_number)})
        sr_status = sr_status_response.body
        logger.info(f"sr_status=\n{pprint.pformat((dict(sr_status)))}")

        logger.info("Ending API session")
