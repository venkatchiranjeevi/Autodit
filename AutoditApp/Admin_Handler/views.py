from rest_framework.response import Response
from AutoditApp.mixins import AuthMixin
from AutoditApp.Admin_Handler.dal import ControlHandlerData, FrameworkMasterData, HirerecyMapperData
from rest_framework.views import APIView


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
        frameworks_data = HirerecyMapperData.get_controls_by_framework_id(f_id)
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


class AdminPolicyHandlerAPI(AuthMixin):
    def get(self, request):
        # frameworkid --> get only those polices else get all polices
        pass

    def post(self, request):
        pass


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


