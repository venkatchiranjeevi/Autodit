from boto3 import client as botoclient


<<<<<<< HEAD

class Cognito:
    def __init__(self):
        pass
=======
class Cognito:
    def __init__(self):
        pass

    COGNITO_USERPOOL_ID = ""

>>>>>>> origin/master
    FETCH_COGNITO_TOKEN_CACHE_KEYS = "core:verify_cognito_token:{}"
    COGNITO_CLIENT = 'cognito-idp'
    CLIENT = botoclient(COGNITO_CLIENT,
                        aws_access_key_id="AKIATZFC3A3LGLBZMAKV",
<<<<<<< HEAD
                        aws_secret_access_key="Mmo3Nfa9mgY+6CFxrh+1Gqo1N8F/z+d6VDH7M7r",
=======
                        aws_secret_access_key="oMmo3Nfa9mgY+6CFxrh+1Gqo1N8F/z+d6VDH7M7r",
>>>>>>> origin/master
                        region_name="ap-south-1")

    REFRESH_TOKEN_AUTH_FLOW = 'REFRESH_TOKEN_AUTH'
    AUTH_TYPE = ["COGNITO", "AISATSAD"]  # if future any new auth type came then need to add here
    CONSTANT_TRUE_VALUE = ["true", "True"]
    CONSTANT_FALSE_VALUE = "false"
    MOBILE_NUM_PREFIX = "+91"
    DEFAULT_ROLE = 47
    DEFALUT_AIRPORT = 13
    DEFAULT_ENTITY = 9    #To avoid  errors
