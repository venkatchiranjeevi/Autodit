import razorpay
from datetime import datetime, timedelta
from AutoditApp.models import TenantSubscriptions, SubscriptionBillingDetails, TenantFrameworkMaster, FrameworkMaster


class Subscription:
    @staticmethod
    def createSubscription(data):
        plan_id = data['plan_id']
        selected_frameworks = []
        framework__master_pks = []
        tenant_id = data.get("tenant_id")
        tm = datetime.now() + timedelta(days=2)
        for framework in data['frameworks']:
            framework__master_pks.append(framework['id'])
            selected_frameworks.append(
                {"item": {"name": framework['framework_name'], "amount": 20000, "currency": "INR"}})
        selected_frameworks.remove(0)
        if plan_id == "plan_JjEjWlJkjOPTXe":
            selected_frameworks.clear()
        subscription_data = {"plan_id": plan_id, "total_count": 2, "quantity": 1, "addons": selected_frameworks,
                             "expire_by": int(round(tm.timestamp())), "customer_notify": 0}
        framework_master = FrameworkMaster.objects.filter(id__in=framework__master_pks)
        tenant_frameworks = [];
        for framework_master_var in framework_master:
            tenant_frameworks.append(
                TenantFrameworkMaster(tenant_framework_name=framework_master_var.framework_name,
                                      master_framework_id=framework_master_var.id,
                                      framework_type=framework_master_var.framework_type,
                                      description=framework_master_var.description,
                                      is_deleted=0, is_active=0, tenant_id=tenant_id))
        TenantFrameworkMaster.objects.filter(tenant_id=tenant_id).delete()
        TenantFrameworkMaster.objects.bulk_create(tenant_frameworks)
        print(framework_master)
        if plan_id:
            client = razorpay.Client(auth=("rzp_test_WRFdDZQHEaoM2q", "srk7PllgG016CY2DrczYYPbQ"))
            client.set_app_details({"title": "Autodit", "version": "1.0"})
            try:
                subscription_response = client.subscription.create(subscription_data)
                expire_by = datetime.fromtimestamp(subscription_response.get("expire_by"))
                tenant_subscription = TenantSubscriptions.objects.create(tenant_id=tenant_id,
                                                                         subscription_id=subscription_response.get(
                                                                             "id"),
                                                                         plan_id=subscription_response.get("plan_id"),
                                                                         status="PENDING",
                                                                         expire_by=expire_by)
                SubscriptionBillingDetails.objects.create(tenant_subscription_id=tenant_subscription.id,
                                                          first_name=data['first_name'], last_name=data['last_name'],
                                                          email=data['email'], phone_number=data['phone_number'],
                                                          street_address=data['street_address'],
                                                          city=data['city'], country=data['country'],
                                                          organization=data['organization'],
                                                          gst_number=data['gst_number'])
                return {"status": "SUCCESS", "payment_required": "true",
                        "subscription_id": tenant_subscription.subscription_id}
            except Exception as e:
                print(e)
                return {"status": "FAILURE"}
        else:
            TenantFrameworkMaster.objects.filter(tenant_id=tenant_id).update(is_active=True)
            return {"status": "SUCCESS", "payment_required": "false"}

    @staticmethod
    def handlePaymentSubscription(tenant_id, data):
        try:
            subscription_id = data.get("razorpay_subscription_id")
            payment_id = data.get("razorpay_payment_id")
            tenant_subscription = TenantSubscriptions.objects.get(tenant_id=tenant_id, subscription_id=subscription_id,
                                                                  status="PENDING")
            print(tenant_subscription)
            client = razorpay.Client(auth=("rzp_test_WRFdDZQHEaoM2q", "srk7PllgG016CY2DrczYYPbQ"))
            client.utility.verify_subscription_payment_signature({
                'razorpay_subscription_id': subscription_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': data.get("razorpay_signature")
            })
            tenant_subscription.status = "SUCCESS"
            tenant_subscription.payment_id = payment_id
            tenant_subscription.save()
            TenantFrameworkMaster.objects.filter(tenant_id=tenant_id).update(is_active=True)
            return {"verified": "true"}
        except Exception as e:
            print(e)
            return {"verified": "false"}
