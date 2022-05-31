from AutoditApp.models import ControlMaster, FrameworkMaster


class BaseConstant:
    def __init__(self):
        pass


class ControlHandlerData(BaseConstant):
    @staticmethod
    def get_control_master_data():
        all_controls = ControlMaster.objects.all().values()
        return all_controls

    @staticmethod
    def save_controls_data(data):
        control_master_obj = ControlMaster(control_name=data.get("control_name"), control_type=data.get("control_type"),
                                            description=data.get("description"), is_deleted=False, is_active=True,
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
                                       description= data.get("Description"), is_deleted=False, is_active=True,
                                       created_by= data.get("created_by"))
        framework_obj.save()
        return framework_obj
