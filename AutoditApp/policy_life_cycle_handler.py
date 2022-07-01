import calendar
from collections import defaultdict
from datetime import date, datetime

from django.db.models import Q

from Autodit import settings
from . import dal
from .AWSCognito import Cognito
from AutoditApp.S3_FileHandler import S3FileHandlerConstant
from AutoditApp.core import fetch_data_from_sql_query, get_users_by_tenant_id
from AutoditApp.models import TenantPolicyManager, TenantPolicyParameter, TenantPolicyVersionHistory, \
    TenantGlobalVariables, MetaData, TenantDepartment, TenantControlsCustomTags, TenantPolicyComments, \
    TenantPolicyTasks, TenantPolicyDepartments, TenantPolicyLifeCycleUsers, Roles, PolicyMaster, MasterPolicyParameter


class PolicyLifeCycleHandler:

    @staticmethod
    def get_policy_details_by_policy_id(policy_id):
        policy_details = TenantPolicyManager.objects.get(id=int(policy_id))
        return policy_details

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
        policy_details = PolicyLifeCycleHandler.get_policy_details_by_policy_id(policy_id)
        policy_details.tenant_policy_name = policy_data.get('policyName', policy_details.tenant_policy_name)
        policy_details.summery = policy_data.get('summery', policy_details.summery)
        policy_details.code = policy_data.get('policyCode', policy_details.code)
        # policy_details.review_period = policy_data.get('reviewPeriod', policy_details.review_period)
        policy_details.save()
        published_date = policy_details.published_date
        try:
            pub_date_object = PolicyLifeCycleHandler.add_months(published_date, int(policy_details.review_period))
            pub_date = datetime.strftime(pub_date_object, '%d-%m-%Y')
        except:
            pub_date = ''
        return {"policyId": policy_details.id,
                "policyName": policy_details.tenant_policy_name,
                "policyCode": policy_details.code,
                "policyDescription": policy_details.summery,
                "renewPeriod": policy_details.review_period,
                "nextReviewDate": str(pub_date),
                }

    @staticmethod
    def policy_revision_period_handler(policy_data, policy_id):
        policy_details = TenantPolicyManager.objects.get(id=policy_id)
        policy_details.review_period = policy_data.get('reviewPeriod', policy_details.review_period)
        policy_details.save()
        published_date = policy_details.published_date
        try:
            pub_date = PolicyLifeCycleHandler.add_months(published_date, int(policy_details.review_period))
            pub_date = datetime.strftime(pub_date, '%d-%m-%Y')
        except:
            pub_date = ''
        return {"policyId": policy_details.id,
                "policyName": policy_details.tenant_policy_name,
                "policyCode": policy_details.code,
                "policyDescription": policy_details.summery,
                "reviewPeriod": policy_details.review_period,
                "nextReviewDate": str(pub_date)}

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
    def policy_revision_history_save_handler(policy_data,
                                             policy_details,
                                             policy_id,
                                             tennant_id,
                                             version,
                                             filename,
                                             user_name,
                                             user_id,
                                             action):
        try:
            revision_history = str(eval(policy_data.get('revisionHistory')))
        except:
            revision_history = '{}'
        policy_revision_blob = TenantPolicyVersionHistory.objects.filter(version_type='revisionHistory',
                                                                         policy_id=policy_id,
                                                                         tenant_id=tennant_id,
                                                                         new_version=version).order_by('-id').values()
        if policy_revision_blob:
            policy_revision = policy_revision_blob[0]
            TenantPolicyVersionHistory.objects.filter(id=policy_revision['id']).update(revision_blob=revision_history,
                                                                                       action_performed_by=user_name,
                                                                                       action_performed_by_id=user_id)

            return
        TenantPolicyVersionHistory(tenant_id=tennant_id,
                                   policy_id=policy_id,
                                   tenant_policy_name=policy_details.tenant_policy_name,
                                   old_policy_name=policy_details.policy_file_name,
                                   old_version=str(version),
                                   new_version=str(version),
                                   policy_file_name=filename,
                                   status=policy_details.state,
                                   action_performed=action,
                                   version_type='revisionHistory',
                                   action_performed_by=user_name,
                                   action_performed_by_id=user_id,
                                   action_date=datetime.now(),
                                   revision_blob=str(revision_history)).save()


    @staticmethod
    def policy_content_details_handler(policy_data, policy_id, tennant_id, user_name, user_id):
        updated_content = policy_data.get('policyContent')
        policy_details = TenantPolicyManager.objects.get(id=policy_id)
        try:
            version = policy_details.version
        except:
            version = 1
        # new_version = round(version + 0.1, 2)
        old_content = S3FileHandlerConstant.read_s3_content(policy_details.policy_file_name)
        file_names = policy_details.policy_file_name.split('/')
        file_name = '{root}/{tenant_id}/{policyId}/{version}/{file_name}'
        file_name = file_name.format(root=file_names[0],
                                     tenant_id=str(tennant_id),
                                     policyId=str(policy_id),
                                     version=str(version),
                                     file_name=file_names[-1])
        PolicyLifeCycleHandler.policy_revision_history_save_handler(policy_data,
                                                                    policy_details,
                                                                    policy_id,
                                                                    tennant_id,
                                                                    version,
                                                                    file_name,
                                                                    user_name,
                                                                    user_id,
                                                                    'Save as Draft')
        version_url = S3FileHandlerConstant.upload_s3_file(old_content, policy_details.policy_file_name)
        new_content_url = S3FileHandlerConstant.upload_s3_file(updated_content, file_name)
        TenantPolicyVersionHistory(tenant_id=tennant_id,
                                   policy_id=policy_id,
                                   tenant_policy_name=policy_details.tenant_policy_name,
                                   old_policy_name=policy_details.policy_file_name,
                                   old_version=str(version),
                                   new_version=str(version),
                                   policy_file_name=file_name,
                                   status=policy_details.state,
                                   action_performed='Save as Draft',
                                   version_type='track',
                                   action_performed_by=user_name,
                                   action_performed_by_id=user_id,
                                   action_date=datetime.now()).save()
        policy_details.version = version
        policy_details.policy_file_name = file_name
        policy_details.policy_reference = new_content_url
        policy_details.version = str(version)
        policy_details.save()

    @staticmethod
    def get_version_history_details(policy_id, tenant_id, version_id):
        version_history = TenantPolicyVersionHistory.objects.get(id=version_id)
        policy_details = TenantPolicyManager.objects.get(id=policy_id)
        version_content = S3FileHandlerConstant.read_s3_content(version_history.policy_file_name)
        policy_content = S3FileHandlerConstant.read_s3_content(policy_details.policy_file_name)
        template_variables = PolicyLifeCycleHandler.get_template_parameters(policy_id, tenant_id)
        return {'versionContent': version_content,
                'policyContent': policy_content,
                'templateVariables': template_variables,
                'revisionHistory': version_history.revision_blob}

    @staticmethod
    def get_policy_version_history(policy_id, tennant_id):
        meta_details = MetaData.objects.filter(category='POLICYSTATUS').values('id', 'key', 'display_name', 'next',
                                                                               'prev', 'state_display_name')
        formatted_meta = {meta.get('key'): meta for meta in meta_details}
        query = Q(policy_id=policy_id) & Q(tenant_id=tennant_id)
        query = query & Q(version_type='revisionHistory')
        history_objects = TenantPolicyVersionHistory.objects.filter(query).values().order_by('-action_date')
        history_details = []
        for history in history_objects:
            action_details = formatted_meta.get(history.get('status'))
            details = {'versionId': history.get('id'),
                       'policyId': history.get('policy_id'),
                       'policyName': history.get('tenant_policy_name'),
                       'oldVersion': history.get('old_version'),
                       'newVersion': history.get('new_version'),
                       'revisionHistory': history.get('revision_blob'),
                       'status': 'Approved' if history.get('status') == 'PUB' else 'Pending',
                       'actionPerformed': action_details.get('display_name'),
                       'actionPerformedBy': history.get('action_performed_by'),
                       'actionPerformedDate': history.get('action_date')}
            history_details.append(details)
        return history_details

    @staticmethod
    def add_months(sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    @staticmethod
    def comments_add_handler(tenant_id, data):
        updated_comment = data.get('commentObject')
        policy_id = data.get('policyId')
        comments_obj, created = TenantPolicyComments.objects.get_or_create(tenant_id=tenant_id,
                                                                           tenant_policy_id=policy_id)
        comments_obj.comment = str(updated_comment)
        comments_obj.save()
        return True

    @staticmethod
    def get_eligible_users(policy_id, tenant_id):
        all_users = Cognito.get_all_cognito_users_by_userpool_id(settings.COGNITO_USERPOOL_ID)
        tenant_users = get_users_by_tenant_id(all_users, tenant_id)
        query = "SELECT r.RoleId, r.role_name, r.Code, r.DepartmentId from Roles r Inner Join TenantPolicyDepartments " \
                "tp on tp.TenantDepartment_id = r.DepartmentId  where tp.tenant_id = {t_id} and tp.TenantPolicyID = {" \
                "p_id}  and tp.isActive=1".format(t_id=tenant_id, p_id=policy_id)
        roles = fetch_data_from_sql_query(query)
        role_ids = [role.get('RoleId') for role in roles]
        elgible_users = []
        for user in tenant_users:
            role_details = user.get('role_details')
            user_roles = {role.get('role_id'): role.get('role_name') for role in role_details}

            if set(user_roles.keys()).intersection(set(role_ids)):
                elgible_users.append({'userName': user.get('name'),
                                      "userCode": user.get('name')[:2],
                                      "userEmail": user.get('email'),
                                      "userId": user.get('userid'),
                                      "asignedRoles": list(user_roles.values())})
        return elgible_users

    @staticmethod
    def get_policy_states(policy_present_state):
        meta_details = MetaData.objects.filter(category='POLICYSTATUS').values('id', 'key', 'display_name', 'next',
                                                                               'prev', 'state_display_name')
        formatted_meta = {meta.get('key'): meta for meta in meta_details}
        present_state = formatted_meta.get(policy_present_state)
        try:
            next_details = eval(str(present_state.get('next')))
        except:
            next_details = None
        try:
            prev_details = eval(str(present_state.get('prev')))
        except:
            prev_details = None
        present_details = {'stateId': policy_present_state, 'status': 1,
                           'displayText': present_state.get('state_display_name')}
        return prev_details, present_details, next_details

    @staticmethod
    def policy_submit(tenant_id, policy_details, data, user):
        user_email = user.email
        policy_id = policy_details.id
        policy_present_state = policy_details.state
        pending_tasks = TenantPolicyTasks.objects.filter(tenant_id=tenant_id,
                                                         policy_id=policy_id,
                                                         policy_state=policy_present_state,
                                                         task_status=0).values()
        if not pending_tasks:
            return True
        for task in pending_tasks:
            if task.get('user_email') == user_email:
                TenantPolicyTasks.objects.filter(id=task.get('id')).update(task_status=1,
                                                                           task_performed_on=datetime.now(),
                                                                           task_performed_by=user_email)
        pending_tasks = TenantPolicyTasks.objects.filter(tenant_id=tenant_id,
                                                         policy_id=policy_id,
                                                         policy_state=policy_present_state,
                                                         task_status=0).values()
        return True if not pending_tasks else False

    @staticmethod
    def policy_state_tasks_check(tenant_id, policy_details, data, user, status):
        user_email = user.email
        role_details = eval(user.role_id)
        role_details = Roles.objects.filter(role_id__in=role_details).values('role_type')
        role_types = [role.get('role_type') for role in role_details]
        policy_id = policy_details.id
        policy_present_state = policy_details.state
        display_text = data.get('displayText')
        if 'Reject' in display_text or not status:
            # COMPLETE ALL PendING TASKS
            TenantPolicyTasks.objects.filter(tenant_id=tenant_id,
                                             policy_id=policy_id,
                                             task_status=0).update(task_status=2,
                                                                   task_performed_by=user_email,
                                                                   task_performed_on=datetime.now())

            return True
        pending_tasks = TenantPolicyTasks.objects.filter(tenant_id=tenant_id,
                                                         policy_id=policy_id,
                                                         policy_state=policy_present_state,
                                                         task_status=0).values()
        if not pending_tasks:
            return True

        # query = Q()
        for task in pending_tasks:
            if task.get('user_email') == user_email:
                # TODO change to bulk update later
                if task.get('task_type') == 'any':
                    TenantPolicyTasks.objects.filter(tenant_id=tenant_id,
                                                     policy_id=policy_id,
                                                     policy_state=policy_present_state,
                                                     task_status=0).update(task_status=1,
                                                                           task_performed_by=user_email,
                                                                           task_performed_on=datetime.now())
                    break
                else:
                    TenantPolicyTasks.objects.filter(id=task.get('id')).update(task_status=1,
                                                                               task_performed_on=datetime.now(),
                                                                               task_performed_by=user_email)

            elif not task.get('user_email'):
                allowed_role = set(eval(task.get('allowed_roles')))
                if allowed_role.intersection(set(role_types)):
                    if task.get('task_type') == 'any':
                        TenantPolicyTasks.objects.filter(tenant_id=tenant_id,
                                                         policy_id=policy_id,
                                                         policy_state=policy_present_state,
                                                         task_status=0).update(task_status=1,
                                                                               task_performed_on=datetime.now(),
                                                                               task_performed_by=user_email)

                        break
                    else:
                        TenantPolicyTasks.objects.filter(id=task.get('id')).update(task_status=1,
                                                                                   task_performed_on=datetime.now(),
                                                                                   task_performed_by=user_email)
            else:
                print('Different user task')

        pending_tasks = TenantPolicyTasks.objects.filter(tenant_id=tenant_id,
                                                         policy_id=policy_id,
                                                         policy_state=policy_present_state,
                                                         task_status=0).values()
        return True if not pending_tasks else False

    @staticmethod
    def policy_task_creation(tenant_id, policy_details, data, user_email, next_state):
        policy_id = policy_details.id
        department_details = TenantPolicyDepartments.objects.filter(tenant_id=tenant_id,
                                                                    tenant_policy_id=policy_id,
                                                                    is_active=1).values()
        task_type_obj = MetaData.objects.get(category='POLICYSTATUS', key=next_state)
        user_type = task_type_obj.access_user
        policy_users = TenantPolicyLifeCycleUsers.objects.filter(tenant_id=tenant_id,
                                                                 policy_id=policy_id,
                                                                 owner_type=user_type,
                                                                 is_active=1).values()
        if not policy_users:
            department_tasks = []
            for department in department_details:
                department_id = department.get('tenant_dep_id')
                department_tasks.append(TenantPolicyTasks(policy_id=policy_id,
                                                          tenant_id=tenant_id,
                                                          department_id=department_id,
                                                          task_name=task_type_obj.state_display_name,
                                                          policy_state=next_state,
                                                          allowed_roles=task_type_obj.state_user,
                                                          task_type=task_type_obj.task_verify))
            TenantPolicyTasks.objects.bulk_create(department_tasks)

        else:
            user_tasks = []
            for user in policy_users:
                user_email = user.get('owner_email')
                user_tasks.append(TenantPolicyTasks(policy_id=policy_id,
                                                    tenant_id=tenant_id,
                                                    task_name=task_type_obj.state_display_name,
                                                    policy_state=next_state,
                                                    department_id=0,
                                                    task_type=task_type_obj.task_verify,
                                                    user_email=user_email,
                                                    user_id=user.get('owner_user_id')))
            TenantPolicyTasks.objects.bulk_create(user_tasks)

    @staticmethod
    def get_or_create_policy_content(tenant_policy_details, tennat_id):
        if not tenant_policy_details.policy_file_name:
            master_policy_details = PolicyMaster.objects.get(id=tenant_policy_details.parent_policy_id)
            content = S3FileHandlerConstant.read_s3_content(master_policy_details.policy_file_name)
            file_names = master_policy_details.policy_file_name.split('/')
            file_name = '{root}/{tenant_id}/{policyId}/{version}/{file_name}'
            file_name = file_name.format(root=file_names[0],
                                         tenant_id=str(tennat_id),
                                         policyId=str(tenant_policy_details.id),
                                         version=str(1),
                                         file_name=file_names[-1])
            reference = S3FileHandlerConstant.upload_s3_file(content, file_name)
            tenant_policy_details.policy_file_name = file_name
            tenant_policy_details.version = '1'
            tenant_policy_details.save()
            policy_parameters = MasterPolicyParameter.objects.filter(
                policy_id=tenant_policy_details.parent_policy_id).values('type',
                                                                         'parameter_key',
                                                                         'parameter_type',
                                                                         'parameter_value',
                                                                         'description')
            parameters = []
            for parameter in policy_parameters:
                tp = TenantPolicyParameter(tenant_id=tennat_id,
                                           policy_id=tenant_policy_details.id,
                                           parameter_key=parameter.get('parameter_key'),
                                           parameter_type=parameter.get('parameter_type'),
                                           parameter_value=parameter.get('parameter_value'),
                                           description=parameter.get('description'),
                                           is_active=1)
                parameters.append(tp)
            TenantPolicyParameter.objects.bulk_create(parameters)
        #     Add template variables
        return S3FileHandlerConstant.read_s3_content(tenant_policy_details.policy_file_name)

    @staticmethod
    def get_policy_revision_blob(policy_id, tennant_id, version):
        policy_revision_blob = TenantPolicyVersionHistory.objects.filter(version_type='revisionHistory',
                                                                         policy_id=policy_id,
                                                                         tenant_id=tennant_id,
                                                                         new_version=version).order_by('-id').values()
        revision_blob = '{}'
        if policy_revision_blob:
            policy_revision = policy_revision_blob[0]
            revision_blob = policy_revision.get('revision_blob')
        return revision_blob



    @staticmethod
    def get_complete_policy_details(policy_id, tenant_id):
        global_varialbles = TenantGlobalVariables.objects.get(tenant_id=int(tenant_id))
        try:
            gb = eval(global_varialbles.result)
        except:
            gb = {}
        policy_details = TenantPolicyManager.objects.get(id=int(policy_id), tenant_id=tenant_id)
        # TODO need to find if policy content exists
        policy_content = PolicyLifeCycleHandler.get_or_create_policy_content(policy_details, tenant_id)
        departments = dal.PolicyDepartmentsHandlerData.get_departments_by_policy_id(tenant_id, policy_id)
        eligible_users = PolicyLifeCycleHandler.get_eligible_users(policy_id, tenant_id)
        published_date = policy_details.published_date
        try:
            pub_date = PolicyLifeCycleHandler.add_months(published_date, int(policy_details.review_period))
            pub_date = datetime.strftime(pub_date, '%d-%m-%Y')
        except:
            pub_date = ''
        try:
            comment_details = TenantPolicyComments.objects.filter(tenant_policy_id=policy_id,
                                                                  tenant_id=tenant_id).values('comment')[0]
            comment = eval(comment_details['comment'])
        except:
            comment = []
        # TODO find next review date
        prev, present, next = PolicyLifeCycleHandler.get_policy_states(policy_details.state)
        users = dal.TenantPolicyLifeCycleUsersData.get_assigned_users_by_policy_id(tenant_id, policy_id)
        approvers = []
        assignees = []
        reviewers = []

        for each_user in users:
            owner_type = each_user.get("owner_type")
            if owner_type == "assignee" or owner_type == "editor":
                assignees.append(each_user)
            elif owner_type == "approver":
                approvers.append(each_user)
            elif owner_type == "reviewer":
                reviewers.append(each_user)

        return {
            "policyId": policy_id,
            "policyName": policy_details.tenant_policy_name,
            "policyCode": policy_details.code,
            "policyDescription": policy_details.summery,
            "policyContent": policy_content,
            "policyVersion": policy_details.version,
            "policyPresentState": present,
            "nextState": next,
            "prevState": prev,
            "assignees": assignees,
            "editors": assignees,
            "approves": approvers,
            "reviewer": reviewers,
            "renewPeriod": policy_details.review_period,
            "nextReviewDate": str(pub_date),
            'policyComments': comment,
            "policyTags": dal.TenantPolicyCustomTagsData.get_policy_tags(policy_id, tenant_id),
            "departments": departments,
            "revisionHistory": PolicyLifeCycleHandler.get_policy_revision_blob(policy_id,
                                                                               tenant_id,
                                                                               policy_details.version),
            "policyControls": [{"id": 1,
                                "frameworkId": 1,
                                "controlCode": "code",
                                "controlName": "4.1 Understanding the organization and its context",
                                "description": "The organization shall determine external and internal issues that are relevant to its purpose and its strategic direction and that affect its ability to achieve the intended result(s) of its quality management system.\nThe organization shall monitor and review information about these external and internal issues.\nNOTE 1 Issues can include positive and negative factors or conditions for consideration.\nNOTE 2 Understanding the external context can be facilitated by considering issues arising from legal,\ntechnological, competitive, market, cultural, social and economic environments, whether international, national,\nregional or local.\nNOTE 3 Understanding the internal context can be facilitated by considering issues related to values, culture,\nknowledge and performance of the organization.",
                                "isActive": 1,
                                "category": None
                                },
                               {
                                   "id": 2,
                                   "frameworkId": 1,
                                   "controlCode": "test",
                                   "controlName": "4.2 Understanding the needs and expectations of in",
                                   "description": "Due to their effect or potential effect on the organization’s ability to consistently provide products and services that meet customer and applicable statutory and regulatory requirements, the organization\nshall determine:\na) the interested parties that are relevant to the quality management system;\nb) the requirements of these interested parties that are relevant to the quality management system.\nThe organization shall monitor and review information about these interested parties and their\nrelevant requirements.",
                                   "isActive": 1,
                                   "category": None
                               }],
            "eligibleUsers": eligible_users,
            "globalVariables": gb,
            "templateVariables": PolicyLifeCycleHandler.get_template_parameters(policy_id, tenant_id)
        }


class MetaDataDetails:

    @staticmethod
    def get_policy_access_users(state):
        meta_data_details = MetaData.objects.filter(key=state).values()
        return meta_data_details

    @staticmethod
    def tenant_meta_data(tenant_id):
        meta_data = {}
        meta_details = MetaData.objects.filter(category__in=['POLICYSTATUS', 'RENEWAL'])
        status_details = []
        review_details = []
        for met in meta_details:
            if met.category == 'POLICYSTATUS':
                status_details.append({'key': met.key,
                                       'displayName': met.display_name,
                                       'next': met.next,
                                       'prev': met.prev,
                                       'state': met.state_display_name,
                                       'stateUser': met.state_user,
                                       'accessUser': met.access_user})
            elif met.category == 'RENEWAL':
                review_details.append({'key': met.key,
                                       'sortKey': int(met.sort_key),
                                       'displayName': met.display_name})

        meta_data['statusDetails'] = status_details
        review_details = sorted(review_details, key=lambda d: d['sortKey'])
        meta_data['reviewCycle'] = review_details
        meta_data['frameworkPolicies'] = MetaDataDetails.tenant_policy_frameworks(tenant_id).values()
        meta_data['departments'] = TenantDepartment.objects.filter(tenant_id=tenant_id).values('id', 'name', 'code')
        meta_data['customTags'] = [t['tag_name'] for t in
                                   TenantControlsCustomTags.objects.filter(tenant_id=tenant_id).filter(
                                       is_active=1).values('tag_name')]
        meta_data['customTags'] = list(set(meta_data.get('customTags', [])))
        return meta_data

    @staticmethod
    def tenant_policy_frameworks(tenant_id):
        query = "select tpm.id as policyId, fm.FrameworkName as f_name, fm.id," \
                " fm.Description, tpm.tenantPolicyName, tpm.version from" \
                " TenantPolicyManager tpm Inner Join FrameworkMaster fm on tpm.MasterFrameworkId = fm.Id " \
                "where tenant_id = {t_id}"
        query = query.format(t_id=tenant_id)
        details = fetch_data_from_sql_query(query)
        result = defaultdict(list)
        for det in details:
            exiting_obj = result.get(det['f_name'], {})
            exiting_obj['frameworkName'] = det['f_name']
            exiting_obj['frameworkId'] = det['id']
            exiting_obj['frameworkDescription'] = det['Description']
            try:
                exiting_obj['policyDetails'].append({'policyName': det['tenantPolicyName'],
                                                     'policyId': det['policyId']})
            except:
                exiting_obj['policyDetails'] = [{'policyName': det['tenantPolicyName'],
                                                 'policyId': det['policyId']}]
            result[det['f_name']] = exiting_obj
        return result
