from collections import defaultdict

from django.forms import model_to_dict
from rest_framework.response import Response
from AutoditApp.mixins import AuthMixin
from AutoditApp.Admin_Handler.dal import ControlHandlerData, FrameworkMasterData, HirerecyMapperData, PolicyMasterData
from AutoditApp.Admin_Handler.sql_queries import policy_master_details, policy_master_by_f_id
from AutoditApp.core import fetch_data_from_sql_query
from rest_framework.views import APIView
from django.db.models import Q


class AdminFrameworkHandlerAPI(AuthMixin):
    def get(self, request):
        master_frameworks = FrameworkMasterData.get_framework_master()
        return Response(master_frameworks)

    def post(self, request):
        data = request.data
        data['created_by'] = request.user.name
        framework_obj = FrameworkMasterData.save_frameworks(data)
        return Response({"meassage": "Framework Added Successfully", "status": True})


class AdminControlHandlerAPI(APIView):
    def get(self, request):
        f_id = request.GET.get("framework_id")
        # Get control with only that framework id
        framework_controls_data = HirerecyMapperData.get_controls_and_policies_by_framework_id(f_id)
        return Response(framework_controls_data)

    def post(self, request):
        data = request.data
        control_master_obj = ControlHandlerData.save_controls_data(data, request.user.pk)
        updated_data = model_to_dict(control_master_obj)
        return Response({"message": "Control added Successfully",
                         'controlData': updated_data,
                         "status": True})


class AdminPolicyHandlerAPI(APIView):
    def get(self, request):
        f_id = request.GET.get("framework_id")
        if f_id:
            where_condition = " where hm.Fid = {} and hm.PolicyId is not NULL".format(f_id)
            query = policy_master_by_f_id.format(where_condition)
        else:
            query = policy_master_details
        policy_details = fetch_data_from_sql_query(query)
        return Response(policy_details)

    def post(self, request):
        data = request.data
        data['created_by'] = request.user.name
        data['user_id'] = request.user.userid
        policy_obj = PolicyMasterData.save_policy_details(data)
        return Response({"status": True, "message": "Policy Added Successfully"})


class AdminControlsBlockDetails(AuthMixin):
    def get(self, request):
        f_id = request.GET.get("framework_id")
        # Get control with only that framework id
        framework_controls_data = HirerecyMapperData.get_controls_framework_block_details(f_id)
        result = defaultdict(list)
        for control_data in framework_controls_data:
            framework_id = control_data['FrameworkId']
            framework_name = control_data['FrameworkName']
            control_details = {
                'ControlName': control_data.get('ControlName'),
                'ControlId': control_data.get('Id'),
                'ControlCode': control_data.get('ControlCode'),
                'ControlDescription': control_data.get('ControlDescription'),
                'IsActive': control_data.get('IsActive'),
            }
            try:
                result[framework_id]['controlDetails'].append(control_details)
            except:
                result[framework_id] = {'frameworkName': framework_name,
                                        'frameworkDescription': control_data.get('FrameworkDescription'),
                                        'controlDetails': [control_details],
                                        'frameworkId': framework_id}
            # result[''] =
        return Response(result.values())


class AdminSinglePolicyHandler(AuthMixin):
    def get(self, request):
        # policyid
        # get policy url get content
        # get policy controls
        # Template variables
        pass

    def post(self, request):
        # Policy Name
        # Poclicy Descrpition
        pass
