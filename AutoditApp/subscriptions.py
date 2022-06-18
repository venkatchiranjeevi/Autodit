import razorpay
from datetime import datetime, timedelta
import calendar


class Subscription:
    @staticmethod
    def createSubscription(data):
        print(data['plan_id'])
        client = razorpay.Client(auth=("rzp_test_WRFdDZQHEaoM2q", "srk7PllgG016CY2DrczYYPbQ"))
        client.set_app_details({"title": "Autodit", "version": "1.0"})
        tm = datetime.now() + timedelta(days=2)
        try:
            subscription_response = client.subscription.create({
                "plan_id": data['plan_id'],
                "total_count": 1,
                "quantity": 1,
                "expire_by": int(round(tm.timestamp())),
                "customer_notify": 0
            })
            return subscription_response.get('id')
        except Exception as e:
            print(e)
        return None
