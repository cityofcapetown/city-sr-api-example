import argparse
import base64
import hashlib
import hmac
import logging
import pprint
import sys
import re

import coct_sr_api_client
from coct_sr_api_client.api import auth_group_api, service_request_group_api
from coct_sr_api_client.models.request_attributes_schema import RequestAttributesSchema

logger = logging.getLogger(__name__)


def validate_reference_number(value):
    if not re.match(r'^9\d{9}$', value):
        raise argparse.ArgumentTypeError('Reference number must be a 10-digit number starting with 9')
    return str(value)


def validate_hex_string(value):
    if not re.match(r'^[0-9a-fA-F]{32}$', value.replace("-", "")):
        raise argparse.ArgumentTypeError('Invalid hex string: must be 32 characters long')
    return str(value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of your program')

    # SR params
    parser.add_argument('-t', '--type', type=int, required=True,
                        help='4 digit numerical type code')
    parser.add_argument('-st', '--subtype', type=int, required=True,
                        help='4 digit numerical subtype code')
    parser.add_argument('-m', '--message', type=str, required=True,
                        help='Message to pass into body of request')
    parser.add_argument('-a', '--address', type=str, required=True,
                        help='Comma separated string description of location of issue')
    parser.add_argument('-y', '--latitude', type=float, required=True,
                        help='Latitude of the issue')
    parser.add_argument('-x', '--longitude', type=float, required=True,
                        help='Longitude of the issue')
    parser.add_argument('-n', '--telephone', type=str, required=True,
                        help='Phone number of the reporter')
    parser.add_argument('-e', '--email', type=str, required=True,
                        help='Email of the reporter')
    parser.add_argument('-c', '--comm', type=str, required=True, choices=["EMAIL", "SMS", "NONE"],
                        help='Communication preference of the reporter. EMAIL refers to email, SMS refers to SMS, and NONE refers to well, none')
    parser.add_argument('-sn', '--street-number', type=str, required=True,
                        help='Street number of the service request.')
    parser.add_argument('-str', '--street', type=str, required=True,
                        help='Street name of the service request.')
    parser.add_argument('-s', '--suburb', type=str, required=True,
                        help='Suburb of the service request.')
    # Non-SR params
    parser.add_argument('-p', '--public-key', type=validate_hex_string, required=True,
                        help='Public key (32 character long UUID)')
    parser.add_argument('-k', '--private-key', type=validate_hex_string, required=True,
                        help='Private key (32 character long UUID)')
    parser.add_argument('-v', '--verbose', action='store_true', required=False,
                        help="Turn on verbose logging")

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s: %(message)s')

    # getting all script args and removing those that aren't SR parameters
    sr_args = vars(args).copy()
    for key in ["verbose", "public_key", "private_key"]:
        del sr_args[key]
    sr_args['username'] = ""  # unused arg in API spec

    request_attrs = RequestAttributesSchema(**sr_args)
    logger.debug(f'Received arguments: {args.public_key=}, args.private_key="{"*" * len(args.private_key)}"')
    logger.debug(f'Received sr_args: {request_attrs=}')

    configuration = coct_sr_api_client.Configuration(
        host="https://qaeservices1.capetown.gov.za/coct/api"
    )
    # Setting the service Identifier
    configuration.api_key['serviceAuth'] = args.public_key.replace("-", "")

    with coct_sr_api_client.ApiClient(configuration) as api_client:
        auth_api_instance = auth_group_api.AuthGroupApi(api_client)
        logger.info("Logging into API")
        login_response = auth_api_instance.zcur_guest_login_get_without_preload_content(
            cookie=args.private_key.replace("-", "")
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

        # Creating the HMAC signature
        message = bytes(request_attrs.to_json(), 'utf-8')
        secret = bytes(args.private_key, 'utf-8')
        signature = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
        configuration.api_key['signatureAuth'] = signature

        # Creating the SR
        sr_api_instance = service_request_group_api.ServiceRequestGroupApi(api_client)
        create_sr_response = sr_api_instance.zsreq_sr_post(request_attrs)
        logger.info(f"SR created successfully - {create_sr_response.reference_number}")

        # Looking up the current state of our newly created SR
        sr_status_response = sr_api_instance.zsreq_sr_reference_no_get(reference_no=create_sr_response.reference_number)
        logger.info(f"sr_status=\n{pprint.pformat((dict(sr_status_response)))}")

        logger.info("Ending API session")
