import pytest
from unittest.mock import Mock
from graphql_jwt.shortcuts import get_token
from prices import Money

from django.test.client import Client
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.utils.encoding import smart_text

from saleor.account.models import Address, User
from saleor.discount.models import Sale
from saleor.checkout.models import Cart
from saleor.product.models import (
    AttributeChoiceValue, Category, Collection, Product, ProductAttribute,
    ProductAttributeTranslation, ProductImage, ProductTranslation, ProductType,
    ProductVariant)
from saleor.checkout.utils import add_variant_to_cart


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
def address(db):  # pylint: disable=W0613
    return Address.objects.create(
        first_name='Mauricio',
        last_name='Collazos',
        company_name='Contraslash S.A.S.',
        street_address_1='Calle 2 Oeste 52 139',
        city='Cali',
        postal_code='760040',
        country='CO',
        phone='+573004579215'
    )


@pytest.fixture
def customer_user(
    address
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
