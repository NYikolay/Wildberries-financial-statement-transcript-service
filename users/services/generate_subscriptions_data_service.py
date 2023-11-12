import json
from typing import List, Dict
from datetime import datetime
import pytz
from payments.forms import RoboKassaForm
from payments.models import SubscriptionType, SubscriptionTypes
from users.models import UserSubscription, UserDiscount
from decimal import Decimal


def generate_robokassa_form(
        request_user,
        cost,
        duration,
        duration_desc,
        subscription_type,
        discount
):
    receipt_json = {
        "items": [
            {
                "name": f"Оплата информационно-аналитических и консалтинговых услуг на портале сервиса commery.ru "
                        f"за {duration} {duration_desc.lower()}",
                "quantity": duration,
                "sum": cost,
                "payment_method": "full_payment",
                "tax": "none"
            }
        ]
    }

    desc_text = f'Оплата подписки Commery.ru на срок {duration} {duration_desc}'
    return RoboKassaForm(initial={
        'Description': desc_text,
        'OutSum': cost,
        'CustomerEmail': request_user.email,
        'Receipt': json.dumps(receipt_json, ensure_ascii=False),
        'UserEmail': request_user.email,
        'SubscriptionType': subscription_type,
        'Discount': discount,
        'Duration': duration,
        'DurationDescription': duration_desc
    })


def get_calculated_subscription_values(subscription_type, current_user_subscription, active_user_discount) -> dict:
    """
    The function calculates the subscription values for the user
    :param subscription_type: Object of a subscription type common to all users
    :param current_user_subscription: The object of the current user subscription, if none, contains None
    :param active_user_discount: The object of a unique discount for the user,
    if it does not exist, contains None
    :return: Dictionary
    """
    build_in_discount: Decimal = active_user_discount.percent if active_user_discount else \
        subscription_type.build_in_discount

    if build_in_discount > 0:
        cost: Decimal = subscription_type.cost - (subscription_type.cost * Decimal((build_in_discount / 100)))
    else:
        cost: Decimal = subscription_type.cost

    cost_for_week: int = round((cost / 4) / subscription_type.duration)

    if current_user_subscription:
        subscribed_to = current_user_subscription.subscribed_to
        build_in_discount = current_user_subscription.discount_percent
    else:
        subscribed_to = None

    return {
        'build_in_discount': build_in_discount,
        'cost': round(cost),
        'cost_for_week': cost_for_week,
        'subscribed_to': subscribed_to,
    }


def get_current_user_subscription_data(request_user, active_user_discount) -> None or dict:
    current_user_subscription = UserSubscription.objects.filter(
        user=request_user,
        subscribed_to__gt=datetime.now()
    ).first()

    if not current_user_subscription:
        return None

    current_subscription_values = get_calculated_subscription_values(
        current_user_subscription.subscription_type, current_user_subscription, active_user_discount
    )
    current_subscription = {
        'type': current_user_subscription.subscription_type.type,
        'duration': current_user_subscription.subscription_type.duration,
        'duration_desc': current_user_subscription.subscription_type.duration_desc,
        **current_subscription_values,
    }

    return current_subscription


def get_user_subscriptions_data(request_user) -> dict:
    """
    The function generates a list consisting of dictionaries with user-accessible rates and their values,
    based on the SubscriptionType, UserSubscription, UserDiscount models
    :param request_user: Current authorized user
    :return: Returns a list containing the dictionaries
    """
    subscriptions_types = SubscriptionType.objects.exclude(type=SubscriptionTypes.TEST).order_by('duration')

    active_user_discount = UserDiscount.objects.filter(
        user=request_user,
        expiration_date__gt=datetime.now(),
        is_active=True
    ).first()

    current_subscription = get_current_user_subscription_data(request_user, active_user_discount)

    subscriptions_data: List[dict] = []

    for subscription_type in subscriptions_types:
        calculated_subscription_values: dict = get_calculated_subscription_values(
            subscription_type,
            None,
            active_user_discount
        )

        subscriptions_data.append(
            {
                'duration': subscription_type.duration,
                'duration_desc': subscription_type.duration_desc,
                'cost': calculated_subscription_values.get('cost'),
                'cost_for_week': calculated_subscription_values.get('cost_for_week'),
                'build_in_discount': calculated_subscription_values.get('build_in_discount'),
                'form': generate_robokassa_form(
                    request_user,
                    calculated_subscription_values.get('cost'),
                    subscription_type.duration,
                    subscription_type.duration_desc,
                    subscription_type.type,
                    calculated_subscription_values.get('build_in_discount')
                )
            }
        )

    return {"current_subscription": current_subscription, "subscriptions_data": subscriptions_data}



