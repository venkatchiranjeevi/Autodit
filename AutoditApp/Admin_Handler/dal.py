from AutoditApp.models import ControlMaster, FrameworkMaster, HirerecyMapper


class BaseConstant:
    def __init__(self):
        pass


class ControlHandlerData(BaseConstant):
    @staticmethod
    def get_control_master_data_by_control_ids(control_ids):
        all_controls = ControlMaster.objects.filter(id__in=control_ids, is_deleted=False,is_active=True).\
            values("control_name", "control_type", "control_code", "description")
        return all_controls

    @staticmethod
    def save_controls_data(data):
        control_master_obj = ControlMaster(control_name=data.get("control_name"), control_type=data.get("control_type"),
                                            description=data.get("description"), cntrol_code=data.get("control_code"),
                                            is_deleted=False, is_active=True,
                                           created_by=data.get("created_by"))
        control_master_obj.save()
        return control_master_obj


class FrameworkMasterData(BaseConstant):

    @staticmethod
    def get_frameworks_data_by_ids(master_ids):
        master_frameworks = list(FrameworkMaster.objects.filter(id__in=master_ids, is_active=True,
                                                                is_deleted=False).values())
        return master_frameworks

    @staticmethod
    def get_framework_master():
        all_frameworks = FrameworkMaster.objects.all().values()
        return all_frameworks

    @staticmethod
    def save_frameworks(data):
        framework_obj = FrameworkMaster(framework_name=data.get("framework_name"),
                                       framework_type=data.get("framework_type"),
                                       description= data.get("description"), is_deleted=False, is_active=True,
                                       created_by= data.get("created_by"))
        framework_obj.save()
        return framework_obj


class HirerecyMapperData(BaseConstant):

    @staticmethod
    def save_hirerey_mapper_data(hirerecy_data):
        hirerecy_master_obj = HirerecyMapper(f_id=hirerecy_data.get("f_id"), c_id=hirerecy_data.get("c_id"))
        return True

    @staticmethod
    def get_controls_by_framework_id(f_id):
        frameworks_data = list(HirerecyMapper.objects.filter(f_id=f_id).values("id", "f_id", "c_id", "policy_id"))
        return frameworks_data