ROLE_POLICIES = """select r.RoleId , r.role_name ,r.Code ,r.is_active ,rp.accesspolicy_id ,ap.Policy  from Roles r left join 
                  Roles_policies rp  on r.RoleId = rp.roles_id left join AccessPolicy ap on rp.accesspolicy_id = ap.LogId  where r.RoleId in ({}) """

CONTROLS_MASTER = """ select cm.Id as c_id ,ControlCode ,ControlName ,
                      cm.created_by from ControlMaster cm """


TENANT_CONTROL_ID = """select tcm.Id as Tenant_control_Id, tcm.Master_Control_Id  as master_control_id, 
tcm.TenantFrameworkId as tenant_framework_id , tfm.MasterFId  as master_framework_id
                        from TenantControlMaster tcm left join TenantFrameworkMaster tfm on tcm.TenantFrameworkId =tfm.Id 
                        where  TenantFrameworkId in ({}) """