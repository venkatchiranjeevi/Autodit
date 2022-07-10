from boto3 import client as botoclient
from django.conf import settings
from time import time as current_time
from AutoditApp.models import Users


User_Exist_Exception = "An error occurred (UsernameExistsException) " \
                       "when calling the AdminCreateUser operation: User account already exists"
PASSWOIRD_POLICY = "'An error occurred (InvalidPasswordException) when calling the AdminCreateUser operation: " \
                   "Password did not conform with password policy: Password must have uppercase characters'"

DEFAULT_POLICIES = ['views', 'actions']
DEFAULT_VIEWS = ["Dashboard", "Settings", "Admin", "M_ITM_DASH","M_ITM_PLCM", "M_ITM_PLCM", "M_ITM_CTRLM",
                 "M_ITM_EVDCM","M_ITM_CALDM", "M_ITM_STNGS"]

EDITIOR_VIEWS = ["M_ITM_DASH","M_ITM_PLCM"]

ADMIN_ACTIONS = ["POLICY_EDIT", "POLICY_COMMENT", "POLICY_VIEW", "POLICY_SEND_TO_APPROVAL", "POLICY_PUBLISH", "POLICY_USER_SETTINGS", "POLICY_TAGS_MODIFY", "POLICY_DEPT_M", "POLICY_REV_CYCLE_M"]

EDITOR_ACTIONS = ["POLICY_EDIT", "POLICY_VIEW", "POLICY_COMMENT", "POLICY_TAGS_MODIFY"]

REVIEWER_ACTIONS = ["POLICY_EDIT", "POLICY_COMMENT", "POLICY_VIEW", "POLICY_SEND_TO_APPROVAL", "POLICY_TAGS_MODIFY"]

APPROVER_ACTIONS = ["POLICY_EDIT", "POLICY_COMMENT", "POLICY_VIEW", "POLICY_SEND_TO_APPROVAL", "POLICY_PUBLISH", "POLICY_TAGS_MODIFY", "POLICY_REV_CYCLE_M"]

ACTIONS_DATA = {'Editor': EDITOR_ACTIONS, 'Reviewer': REVIEWER_ACTIONS, 'Approver': APPROVER_ACTIONS, 'Admin': ADMIN_ACTIONS}

TENANT_LOGOS_BUCKET = "autodit-development-app"
S3_ROOT = "https://autodit-development-app.s3.ap-south-1.amazonaws.com/{}"
#
# class Cognito:
#
#     def __init__(self):
#         pass
#
#
#     CLIENT = botoclient('cognito-idp',
#                         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#
#                         aws_secret_access_key=settings.AWS_SECRET_KEY,
#
#                         region_name=settings.REGION)
#
#     REFRESH_TOKEN_AUTH_FLOW = 'REFRESH_TOKEN_AUTH'
#     CONSTANT_TRUE_VALUE = ["true", "True"]
#     CONSTANT_FALSE_VALUE = "false"
#     MOBILE_NUM_PREFIX = "+91"
#
#     @staticmethod
#     def claims_token(access_token):
#         """Taking access_token as input and decode the token and return user info from access_token"""
#         claims = jwt.get_unverified_claims(access_token)
#         return claims
#
#     @staticmethod
#     def verify_cognito_token(session_key):
#         try:
#             headers = jwt.get_unverified_headers(session_key)
#         except JWTError:
#             return False, "Invalid Token Headders"
#         kid = headers.get("kid")
#         key_index = -1
#         keys = settings.COGNITO_USERPOOL_KEYS
#         for i in range(len(keys)):
#             if kid == keys[i]['kid']:
#                 key_index = i
#                 break
#         if key_index == -1:
#             return False, 'Invalid Token Keys'
#         public_key = jwk.construct(keys[key_index])
#         message, encoded_signature = str(session_key).rsplit('.', 1)
#         decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
#         if not public_key.verify(message.encode("utf8"), decoded_signature):
#             return False, 'Invalid Token Signature'
#
#         claims = Cognito.claims_token(session_key)
#
#         # if current_time() > claims.get('exp'):
#         #     return False, "Token expired"
#         result = True, "Success"
#         timeout = claims.get('exp') - current_time()
#         return result
#
#
#     @staticmethod
#     def map_cognito_to_user(sub):
#         """
#         Taking Input as Cognito Sub value and return Avileap User model related user object
#         """
#         user_model_dict = {}
#         user_dict = Cognito.CLIENT.list_users(
#             UserPoolId=settings.COGNITO_USERPOOL_ID,
#             Filter='sub^=\"{}\"'.format(sub)
#         )
#         try:
#             user_model_dict['cognito_username'] = user_dict['Users'][0].get('Username', None)
#             user_dict = user_dict["Users"][0]
#         except IndexError as e:
#             return None
#         user_model_dict['markedfordeletion'] = not user_dict.get("Enabled", True)
#         attributes = {}
#         for key in user_dict.get('Attributes'):
#             attributes[key.get('Name')] = key.get('Value')
#         user_model_dict.update(attributes)
#
#         final_model_match = {
#             "userid": sub,
#             "mobnmbr": user_model_dict.get("phone_number", None),
#             "email": user_model_dict.get("email", user_model_dict.get('custom:Email_Address')),
#             "name": user_model_dict.get('name', user_model_dict.get("cognito_username")),
#             "role_id": user_model_dict.get('custom:role_id', None),
#             "department_id": user_model_dict.get('custom:department_id', None),
#             "gender": user_model_dict.get('gender', None),
#             "markedfordeletion": user_model_dict.get('markedfordeletion', None),
#             "username_cognito": user_model_dict.get('cognito_username', None),
#             "gender": user_model_dict.get("gender"),
#             "is_authenticated": True,
#             "is_active": True,
#             "tenant_id" : user_model_dict.get("custom:tenant_id")
#
#             # "_permissions_cache_key": 'permissions_cache',
#             # "_flights_cache_key": 'flights_cache',
#             # "_equipments_cache_key": 'equipments_cache',
#             # "_activities_cache_key": 'activities_cache',
#             # "_views_cache_key": 'views_cache',
#             # "_alerts_cache_key": "alerts_cache"
#         }
#         user = Users()
#         user.__dict__.update(final_model_match)
#         return user
#
#
#     @staticmethod
#     def get_cognito_user(sub):
#         """Taking input as cognito sub and Return user object as Avileap object"""
#         user = Cognito.map_cognito_to_user(sub)
#         return user


class RolesConstant:
    Default_Roles = {'Editor': 'ED', 'Reviewer': 'RV', 'Approver': 'AP'}


