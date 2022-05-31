from AutoditApp.dal import HirerecyMapperData
from rest_framework.response import Response
from AutoditApp.mixins import AuthMixin
from AutoditApp.Admin_Handler.dal import ControlHandlerData, FrameworkMasterData


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
        all_controls = ControlHandlerData.get_control_master_data()
        return Response(all_controls)

    def post(self, request):
        data = request.data
        data['created_by'] = request.user.name
        control_master_obj = ControlHandlerData.save_controls_data(data)
        hirerecy_data = {"c_id": control_master_obj.id, "f_id": data.get("f_id")}
        HirerecyMapperData.save_hirerey_mapper_data(hirerecy_data)
        return Response({"message": "Control added Successfully", "status": True})
