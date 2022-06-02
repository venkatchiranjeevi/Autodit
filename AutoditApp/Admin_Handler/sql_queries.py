policy_master_by_f_id = """ select pm.id ,pm.PolicyName ,pm.Category ,pm.policy_code,fm.Id as framework_id ,fm.FrameworkName
                        from HirerecyMapper hm left join FrameworkMaster 
                         fm on hm.Fid = fm.Id left join PolicyMaster pm on pm.id = hm.PolicyId  
                      {} group by hm.Fid ,hm.PolicyId 
 """
policy_master_details = """select pm.id ,pm.PolicyName ,pm.Category ,pm.policy_code,fm.Id as framework_id ,fm.FrameworkName
                           from PolicyMaster pm left join HirerecyMapper hm on hm.PolicyId = pm.id 
                           left join FrameworkMaster fm on hm.Fid = fm.Id group by pm.id
"""