import random

import factory

from users.models import User, WBApiKey, ClientUniqueProduct, SaleReport, IncorrectReport


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    date_joined = factory.Faker("date_time")
    phone = '+375336186875'
    password = factory.PostGenerationMethodCall('set_password', '12345678')
    is_accepted_terms_of_offer = True
    is_active = True


class WBApiKeyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WBApiKey

    api_key = ''
    name = factory.Faker('company')
    user = factory.SubFactory(UserFactory)
    is_current = True


class ClientUniqueProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClientUniqueProduct

    api_key = factory.SubFactory(WBApiKeyFactory)
    nm_id = factory.Faker("barcode")
    brand = factory.Faker("company")
    image = factory.Faker("uri")
    product_name = factory.Faker("company")


class SaleReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SaleReport

    api_key = factory.SubFactory(WBApiKeyFactory)
    owner = factory.SubFactory(UserFactory)
    realizationreport_id = factory.Faker("credit_card_number")  # Just random numbers in create_card_number
    week_num = random.randint(1, 100)
    year = factory.Faker("year")
    unique_week_uuid = factory.Faker("unix_time")
    month_num = factory.Faker("month")
    create_dt = factory.Faker("date_time_this_decade")
    date_from = factory.Faker("date_time_this_decade")
    date_to = factory.Faker("date_time_this_decade")


class IncorrectReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IncorrectReport

    api_key = factory.SubFactory(WBApiKeyFactory)
    owner = factory.SubFactory(UserFactory)
    realizationreport_id = factory.Faker("credit_card_number")  # Just random numbers in create_card_number
    date_from = factory.Faker("date_time_this_decade")
    date_to = factory.Faker("date_time_this_decade")
