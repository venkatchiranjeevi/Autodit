import json

from AutoditApp.S3_FileHandler import S3FileHandlerConstant
from AutoditApp.models import TenantPolicyManager, TenantPolicyParameter, TenantPolicyVersionHistory, \
    TenantGlobalVariables
from AutoditApp.dal import PolicyDepartmentsHandlerData


class PolicyLifeCycleHandler:

    @staticmethod
    def policy_variables_handler(policy_data, policy_id, tenant_id):
        parameters = policy_data.get('policyParameters', [])
        TenantPolicyParameter.objects.filter(policy_id=policy_id).filter(tenant_id=tenant_id).delete()
        updated_params = []
        for param in parameters:
            updated_params.append(TenantPolicyParameter(tenant_id=tenant_id,
                                                        policy_id=policy_id,
                                                        parameter_key=param.get('keyName'),
                                                        parameter_type=param.get('keyType'),
                                                        parameter_value=param.get('keyValue'),
                                                        is_active=1,
                                                        is_deleted=0))
        if updated_params:
            TenantPolicyParameter.objects.bulk_create(updated_params)
        return PolicyLifeCycleHandler.get_template_parameters(policy_id, tenant_id)

    @staticmethod
    def policy_summery_details_handler(policy_data, policy_id):
        policy_details = TenantPolicyManager.objects.get(id=policy_id)
        policy_details.tenant_policy_name= policy_data.get('policyName', policy_details.tenant_policy_name)
        policy_details.summery = policy_data.get('summery', policy_details.summery)
        policy_details.code=policy_data.get('policyCode', policy_details.code)
        policy_details.review_period = policy_data.get('reviewPeriod', policy_details.review_period)
        policy_details.save()
        return {"policyId": policy_details.id,
                "policyName": policy_details.tenant_policy_name,
                "policyCode": policy_details.code,
                "policyDescription": policy_details.summery}

    @staticmethod
    def get_template_parameters(policy_id, tenant_id):
        updated_records = TenantPolicyParameter.objects.filter(policy_id=policy_id).filter(tenant_id=tenant_id).values(
            'parameter_key',
            'parameter_type',
            'parameter_value')
        policy_params = [{"keyName": record.get('parameter_key'),
                          "keyType": record.get('parameter_type'),
                          "keyValue": record.get('parameter_value')} for record in updated_records]
        return policy_params

    @staticmethod
    def policy_content_details_handler(policy_data, policy_id, tennant_id):
        updated_content = policy_data.get('policyContent')
        policy_details = TenantPolicyManager.objects.get(id=policy_id)
        try:
            version = int(policy_details.version)
        except:
            version = 1
        new_version = version + 1
        old_content = S3FileHandlerConstant.read_s3_content(policy_details.policy_file_name)
        file_names = policy_details.policy_file_name.split('/')
        file_name = '{root}/{tenant_id}/{version}/{file_name}'
        file_name = file_name.format(root=file_names[0],
                                     tenant_id=str(tennant_id),
                                     version=str(new_version),
                                     file_name=file_names[-1])
        version_url = S3FileHandlerConstant.upload_s3_file(old_content, file_name)
        new_content_url = S3FileHandlerConstant.upload_s3_file(updated_content, policy_details.policy_file_name)
        policy_details.version = version
        policy_details.policy_reference = new_content_url
        policy_details.save()
        TenantPolicyVersionHistory(tenant_id=tennant_id,
                                   policy_id=policy_id,
                                   tenant_policy_name=policy_details.tenant_policy_name,
                                   old_version=str(version),
                                   new_version=str(new_version),
                                   policy_file_name=file_name).save()

    @staticmethod
    def get_complete_policy_details(policy_id, tenant_id):
        # Policy Details
        # Controls
        global_varialbles = TenantGlobalVariables.objects.get(tenant_id=int(tenant_id))
        try:
            gb = json.loads(global_varialbles.result)
        except:
            gb = {}
        policy_details = TenantPolicyManager.objects.get(id=int(policy_id))
        policy_content = S3FileHandlerConstant.read_s3_content(policy_details.policy_file_name)
        departments = PolicyDepartmentsHandlerData.get_departments_by_policy_id(tenant_id, policy_id)
        users = None
        # TODO find next review date
        return {
            "policyId": policy_id,
            "policyName": policy_details.tenant_policy_name,
            "policyCode": policy_details.code,
            "policyDescription": policy_details.summery,
            "policyContent": policy_content,
            "policyVersion": policy_details.version,
            "polcyPresentState": policy_details.state,
            "nextState": "Review",
            "PrevState": None,
            "assignee": policy_details.editor,
            "approver": policy_details.approver,
            "reviewer": policy_details.reviewer,
            "nextReviewData": "2023-02-01",
            'policyComments': [],
            "policyTags": [],
            "departments": departments,
            "policyControls": [],
            "eligibleUsers": [],
            "globalVariables": gb,
            "templateVariables": PolicyLifeCycleHandler.get_template_parameters(policy_id, tenant_id),
        }






