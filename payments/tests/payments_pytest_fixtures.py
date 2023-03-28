import pytest


@pytest.fixture
def test_robokassa_login():
    return 'com123op'


@pytest.fixture
def test_robokassa_password_1():
    return 'm5LQps4gJmIx9KXuI18Y'


@pytest.fixture
def test_robokassa_password_2():
    return 'k5LUps4gYmIx9LXuJ18N'


@pytest.fixture
def test_robokassa_shp_params():
    return [
        'Shp_discount=0',
        'Shp_duration=1',
        'Shp_durationdesc=Неделя',
        'Shp_type=TEST',
        'Shp_user=admin@mail.ru'
    ]

