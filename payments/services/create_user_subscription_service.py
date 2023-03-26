import decimal
from datetime import datetime
import pytz

from django.db import transaction

from payments.models import SubscriptionType
from payments.services.generating_subscribed_to_date import get_subscribed_to_date
from users.models import UserSubscription


def create_user_subscription(
        current_user,
        sub_type: str,
        total_cost: decimal,
        duration: int,
        duration_description: str,
        discount: decimal,
):
    with transaction.atomic():
        subscription_type_obj = SubscriptionType.objects.get(type=sub_type)

        UserSubscription.objects.create(
            subscription_type=subscription_type_obj,
            user=current_user,
            subscribed_from=datetime.now(),
            total_cost=total_cost,
            subscribed_to=get_subscribed_to_date(
                duration,
                duration_description
            ),
            discount_percent=discount,
        )
