from boto3 import client as botoclient


class Cognito:
    def __init__(self):
        pass

class Cognito:
    def __init__(self):
        pass

    COGNITO_USERPOOL_ID = "ap-south-1_rlvv48z1c"

    FETCH_COGNITO_TOKEN_CACHE_KEYS = "core:verify_cognito_token:{}"
    COGNITO_CLIENT = 'cognito-idp'
    CLIENT = botoclient(COGNITO_CLIENT,
                        aws_access_key_id="AKIATZFC3A3LGLBZMAKV",

                        aws_secret_access_key="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",

                        region_name="ap-south-1")

    REFRESH_TOKEN_AUTH_FLOW = 'REFRESH_TOKEN_AUTH'
    AUTH_TYPE = ["COGNITO", "AISATSAD"]  # if future any new auth type came then need to add here
    CONSTANT_TRUE_VALUE = ["true", "True"]
    CONSTANT_FALSE_VALUE = "false"
    MOBILE_NUM_PREFIX = "+91"

