import razorpay
from datetime import datetime, timedelta
from AutoditApp.models import TenantSubscriptions, SubscriptionBillingDetails


class Subscription:
    @staticmethod
    def createSubscription(data):
        plan_id = data['plan_id'];
        if plan_id:
            client = razorpay.Client(auth=("rzp_test_WRFdDZQHEaoM2q", "srk7PllgG016CY2DrczYYPbQ"))
            client.set_app_details({"title": "Autodit", "version": "1.0"})
            tm = datetime.now() + timedelta(days=2)
            selected_frameworks = []
            for framework in data['frameworks']:
                selected_frameworks.append({"item": {"name": framework['name'], "amount": 200, "currency": "INR"}})
            subscription_data = {"plan_id": plan_id, "total_count": 2, "quantity": 1, "addons": selected_frameworks,
                                 "expire_by": int(round(tm.timestamp())), "customer_notify": 0}
            try:
                subscription_response = client.subscription.create(subscription_data)
                expire_by = datetime.fromtimestamp(subscription_response.get("expire_by"));
                tenant_subscription = TenantSubscriptions.objects.create(tenant_id=data.get("tenant_id"),
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
            return {"status": "SUCCESS", "payment_required": "false"}
