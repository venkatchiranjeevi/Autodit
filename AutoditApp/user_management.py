from rest_framework.views import APIView
from AutoditApp.constants import Cognito
from django.conf import settings
from rest_framework.response import Response


class UsersList(APIView):

    @staticmethod
    def add_new_user_to_cognito_userpool(new_user_data):
        role = new_user_data.get("role_id")
        ph_num = new_user_data.get("mobnmbr")
        email = new_user_data.get("email")
        attributes = [
            {"Name": 'custom:role_id', "Value": str(role)},
            {"Name": 'gender', "Value": new_user_data.get("gender")},
            {"Name": 'name', "Value": new_user_data.get("name")},
            {"Name": 'nickname', "Value": new_user_data.get("nickname")},
            ]
        if ph_num and ph_num != "":
            ph_num = "{var1}{var2}".format(var1=Cognito.MOBILE_NUM_PREFIX, var2=new_user_data.get("mobnmbr"))
            attributes.append({"Name": 'phone_number', "Value": ph_num})
        if email:
            attributes.append({"Name": 'email', "Value": new_user_data.get("email")})
            attributes.append({"Name": 'email_verified', "Value": 'false'})
        response = Cognito.CLIENT.admin_create_user(
            UserPoolId=settings.COGNITO_USERPOOL_ID,
            Username=new_user_data.get("name"),
            UserAttributes=attributes,
            TemporaryPassword=new_user_data.get("password"),
            ForceAliasCreation=True,
           DesiredDeliveryMediums=["EMAIL"])

        return response

    def post(self, request):
        new_user_data = request.data

        response = UsersList.add_new_user_to_cognito_userpool(new_user_data)
        return Response(response)



