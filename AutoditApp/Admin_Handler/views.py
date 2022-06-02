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


class AdminControlHandlerAPI(AuthMixin):
    def get(self, request):
        f_id = request.GET.get("framework_id")
        # Get control with only that framework id
        frameworks_data = HirerecyMapperData.get_controls_and_policies_by_framework_id(f_id)
        control_ids = [each_frame.get("c_id") for each_frame in frameworks_data]
        all_controls = ControlHandlerData.get_control_master_data_by_control_ids(control_ids)
        return Response(all_controls)

    def post(self, request):
        data = request.data
        data['created_by'] = request.user.name
        control_master_obj = ControlHandlerData.save_controls_data(data)
        hirerecy_data = {"c_id": control_master_obj.id, "f_id": data.get("f_id")}
        HirerecyMapperData.save_hirerey_mapper_data(hirerecy_data)
        return Response({"message": "Control added Successfully", "status": True})


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


