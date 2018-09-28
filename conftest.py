import pytest
from unittest.mock import Mock
from graphql_jwt.shortcuts import get_token
from prices import Money

from django.test.client import Client
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.utils.encoding import smart_text
from django_countries.fields import Country
from django_countries import countries
from django.conf import settings
from django_prices_vatlayer.utils import get_tax_for_rate

from saleor.account.models import Address, User
from saleor.discount.models import Sale, Voucher
from saleor.checkout.models import Cart
from saleor.product.models import (
    AttributeChoiceValue,
    Category,
    Product,
    ProductAttribute,
    ProductType,
    ProductVariant
)
from saleor.checkout.utils import add_variant_to_cart
from saleor.shipping.models import (
    ShippingMethod,
    ShippingMethodType,
    ShippingZone
)


class ApiClient(Client):
    """GraphQL API client."""

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        self.user = user
        self.token = get_token(user)
        super().__init__(*args, **kwargs)

    def _base_environ(self, **request):
        environ = super()._base_environ(**request)
        environ.update({'HTTP_AUTHORIZATION': 'JWT %s' % self.token})
        return environ

@pytest.fixture
def default_country(db):
    return Country(settings.DEFAULT_COUNTRY)

@pytest.fixture
def address(
    db,
    default_country
):  # pylint: disable=W0613
    return Address.objects.create(
        first_name='Mauricio',
        last_name='Collazos',
        company_name='Contraslash S.A.S.',
        street_address_1='Calle 2 Oeste 52 139',
        city='Cali',
        postal_code='760040',
        country='PL',
        phone='+573004579215'
    )


@pytest.fixture
def another_address(
    db,
    default_country
):  # pylint: disable=W0613
    return Address.objects.create(
        first_name='Mauricio',
        last_name='Collazos',
        company_name='Contraslash S.A.S.',
        street_address_1='Calle 7 62 A 38',
        city='Cali',
        postal_code='760033',
        country=default_country,
        phone='+573004579215'
    )


@pytest.fixture
def moon_address(
    db
):  # pylint: disable=W0613
    return Address.objects.create(
        first_name='Mauricio',
        last_name='Collazos',
        company_name='Contraslash S.A.S.',
        street_address_1='Moon',
        city='Moon',
        postal_code='',
        country="__",
        phone='+'
    )


@pytest.fixture
def customer_user(
    address,
):  # pylint: disable=W0613
    default_address = address.get_copy()
    user = User.objects.create_user(
        'ma0@contraslash.com',
        'ultra_secret_password',
        default_billing_address=default_address,
        default_shipping_address=default_address
    )
    user.addresses.add(default_address)
    return user


@pytest.fixture
def user_api_client(customer_user):
    return ApiClient(user=customer_user)

@pytest.fixture()
def cart_request_factory(rf, monkeypatch):
    def create_request(user=None, token=None):
        request = rf.get(reverse('home'))
        if user is None:
            request.user = AnonymousUser()
        else:
            request.user = user
        request.discounts = Sale.objects.all()
        request.taxes = None
        monkeypatch.setattr(
            request, 'get_signed_cookie', Mock(return_value=token))
        return request
    return create_request


@pytest.fixture
def cart(db):
    return Cart.objects.create()

@pytest.fixture
def color_attribute(db):  # pylint: disable=W0613
    attribute = ProductAttribute.objects.create(
        slug='color', name='Color')
    AttributeChoiceValue.objects.create(
        attribute=attribute, name='Red', slug='red')
    AttributeChoiceValue.objects.create(
        attribute=attribute, name='Blue', slug='blue')
    return attribute


@pytest.fixture
def size_attribute(db):  # pylint: disable=W0613
    attribute = ProductAttribute.objects.create(slug='size', name='Size')
    AttributeChoiceValue.objects.create(
        attribute=attribute, name='Small', slug='small')
    AttributeChoiceValue.objects.create(
        attribute=attribute, name='Big', slug='big')
    return attribute

@pytest.fixture
def product_type(color_attribute, size_attribute):
    product_type = ProductType.objects.create(
        name='Default Type', has_variants=False, is_shipping_required=True)
    product_type.product_attributes.add(color_attribute)
    product_type.variant_attributes.add(size_attribute)
    return product_type

@pytest.fixture
def category(db):  # pylint: disable=W0613
    return Category.objects.create(name='Default', slug='default')

@pytest.fixture
def product(product_type, category):
    product_attr = product_type.product_attributes.first()
    attr_value = product_attr.values.first()
    attributes = {smart_text(product_attr.pk): smart_text(attr_value.pk)}

    product = Product.objects.create(
        name='Test product', price=Money('10.00', 'USD'),
        product_type=product_type, attributes=attributes, category=category)

    variant_attr = product_type.variant_attributes.first()
    variant_attr_value = variant_attr.values.first()
    variant_attributes = {
        smart_text(variant_attr.pk): smart_text(variant_attr_value.pk)}

    ProductVariant.objects.create(
        product=product, sku='123', attributes=variant_attributes,
        cost_price=Money('1.00', 'USD'), quantity=10, quantity_allocated=1)
    return product


@pytest.fixture
def cart_with_item(
    cart,
    product
):
    variant = product.variants.get()
    add_variant_to_cart(cart, variant, 3)
    cart.save()
    return cart


@pytest.fixture
def tax_rates():
    return {
        'standard_rate': 19,
        'reduced_rates': dict()
    }

@pytest.fixture
def taxes(
    tax_rates
):
    taxes = {
        'standard': {
            'value': tax_rates['standard_rate'],
            'tax': get_tax_for_rate(tax_rates)
        }
    }
    return taxes

@pytest.fixture
def voucher(db):  # pylint: disable=W0613
    return Voucher.objects.create(code='mirumee', discount_value=20)


@pytest.fixture
def cart_with_voucher(
    cart,
    product,
    voucher
):
    variant = product.variants.get()
    add_variant_to_cart(cart, variant, 3)
    cart.voucher_code = voucher.code
    cart.discount_amount = Money('20.00', 'USD')
    cart.save()
    return cart

@pytest.fixture
def shipping_zone(db):  # pylint: disable=W0613
    shipping_zone = ShippingZone.objects.create(
        name='Europe',
        countries=[code for code, name in countries])
    shipping_zone.shipping_methods.create(
        name='DHL',
        minimum_order_price=0,
        type=ShippingMethodType.PRICE_BASED,
        price=10,
        shipping_zone=shipping_zone
    )
    return shipping_zone


@pytest.fixture
def shipping_method(shipping_zone):
    return ShippingMethod.objects.create(
        name='DHL',
        minimum_order_price=0,
        maximum_order_price=1000,
        type=ShippingMethodType.PRICE_BASED,
        price=Money(10, "USD"),
        shipping_zone=shipping_zone
    )


@pytest.fixture
def shipping_method_weight(shipping_zone):
    return ShippingMethod.objects.create(
        name='DHL',
        minimum_order_weight=0,
        maximum_order_weight=10,
        type=ShippingMethodType.WEIGHT_BASED,
        price=Money(10, "USD"),
        shipping_zone=shipping_zone
    )
