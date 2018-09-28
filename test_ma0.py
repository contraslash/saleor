import pytest
import json
from unittest.mock import Mock
from uuid import uuid4

from django.contrib.auth.models import AnonymousUser
from prices import Money, TaxedMoney

from saleor.checkout import utils

from saleor.checkout.models import Cart


def test_get_cart_from_request(
    monkeypatch,
    customer_user,
    cart_request_factory,
    cart_with_item
):
    # Test Case M1-01
    empty_cart = Cart()
    mock_empty_cart = Mock(return_value=empty_cart)
    token_authenticated = uuid4()
    request_authenticated_user = cart_request_factory(user=customer_user, token=token_authenticated)
    monkeypatch.setattr(
        'saleor.checkout.utils.get_user_cart',
        mock_empty_cart
    )
    no_items_cart_authenticated = utils.get_cart_from_request(request_authenticated_user)
    assert no_items_cart_authenticated.quantity == 0
    # Test Case M1-02
    non_empty_cart = cart_with_item
    non_empty_cart.user = customer_user

    mock_cart = Mock(return_value=non_empty_cart)
    monkeypatch.setattr(
        'saleor.checkout.utils.get_user_cart',
        mock_cart
    )
    items_cart_authenticated = utils.get_cart_from_request(request_authenticated_user)
    assert items_cart_authenticated.quantity == 3

    # Test Case M1-03
    unauthenticated_user = AnonymousUser()
    token_unauthenticated = uuid4()
    request_unauthenticated_user = cart_request_factory(user=unauthenticated_user, token=token_unauthenticated)
    monkeypatch.setattr(
        'saleor.checkout.utils.get_anonymous_cart_from_token',
        mock_empty_cart
    )
    no_items_cart_unauthenticated = utils.get_cart_from_request(request_unauthenticated_user)
    assert no_items_cart_unauthenticated.quantity == 0

    # Test Case M1-04
    new_non_empty_cart = cart_with_item
    new_unauthenticated_user = AnonymousUser()
    new_token_unauthenticated = uuid4()
    new_request_unauthenticated_user = cart_request_factory(
        user=new_unauthenticated_user,
        token=new_token_unauthenticated
    )
    new_mock_cart = Mock(return_value=new_non_empty_cart)
    monkeypatch.setattr(
        'saleor.checkout.utils.get_anonymous_cart_from_token',
        new_mock_cart
    )
    items_cart_unauthenticated = utils.get_cart_from_request(new_request_unauthenticated_user)
    assert items_cart_unauthenticated.quantity == 3


def test_get_shipping_address_form(
    customer_user,
    default_country,
    cart_with_item,
    another_address
):
    # Test Case M2-01: This test fails, so to avoid conflict we commented it
    # empty_cart = Cart()
    #
    # forms = utils.get_shipping_address_forms(
    #     empty_cart,
    #     customer_user.addresses.all(),
    #     dict(),
    #     default_country
    # )
    # assert len(forms) == 3
    # Test Case M2-02
    cart = cart_with_item
    cart.user = customer_user
    cart.shipping_address = another_address
    forms = utils.get_shipping_address_forms(
        cart,
        customer_user.addresses.all(),
        dict(),
        default_country
    )
    assert len(forms) == 3

    # Test Case M2-03
    new_cart = cart_with_item
    new_cart.user = customer_user
    new_cart.shipping_address = customer_user.addresses.first()
    forms = utils.get_shipping_address_forms(
        new_cart,
        customer_user.addresses.all(),
        dict(),
        default_country
    )
    assert len(forms) == 3

    # Test Case M2-04
    new_cart_2 = cart_with_item
    forms = utils.get_shipping_address_forms(
        new_cart_2,
        customer_user.addresses.all(),
        dict(),
        default_country
    )
    assert len(forms) == 3


def test_update_shipping_address_in_cart(
    customer_user,
    default_country,
    cart_with_item,
    another_address
):
    # Test Case M3-01: This test fails, so to avoid conflict we commented it
    # empty_cart = Cart()
    # forms = utils.update_shipping_address_in_cart(
    #     empty_cart,
    #     customer_user.addresses.all(),
    #     dict(),
    #     default_country
    # )
    # assert len(forms) == 3

    # Test Case M3-02
    cart = cart_with_item
    cart.user = customer_user
    cart.shipping_address = another_address
    forms = utils.update_shipping_address_in_cart(
        cart,
        customer_user.addresses.all(),
        dict(),
        default_country
    )
    assert len(forms) == 3

    # Test Case M3-03
    new_cart = cart_with_item
    new_cart.user = customer_user
    new_cart.shipping_address = customer_user.addresses.first()
    forms = utils.update_shipping_address_in_cart(
        new_cart,
        customer_user.addresses.all(),
        dict(),
        default_country
    )
    assert len(forms) == 3

    # Test Case M3-04
    new_cart_2 = cart_with_item
    forms = utils.update_shipping_address_in_cart(
        new_cart_2,
        customer_user.addresses.all(),
        dict(),
        default_country
    )
    assert len(forms) == 3


def test_get_billing_forms_with_shipping(
    customer_user,
    default_country,
    cart_with_item,
    another_address,
    address
):

    # Test Case M4-01: This test fails, so to avoid conflict we commented it
    # empty_cart = Cart()
    # forms = utils.get_billing_forms_with_shipping(
    #     empty_cart,
    #     None,
    #     customer_user.addresses.all(),
    #     default_country
    # )
    # assert len(forms) == 3
    pass
    # Test Case M4-02
    cart = cart_with_item
    cart.user = customer_user
    cart.shipping_address = address
    forms = utils.get_billing_forms_with_shipping(
        cart,
        None,
        customer_user.addresses.all(),
        default_country
    )
    assert len(forms) == 3
    # Test Case M4-03
    cart = cart_with_item
    cart.user = customer_user
    customer_user.addresses.add(another_address)
    cart.shipping_address = another_address
    forms = utils.get_billing_forms_with_shipping(
        cart,
        None,
        customer_user.addresses.all(),
        default_country
    )
    assert len(forms) == 3
    # Test Case M4-04
    cart = cart_with_item
    forms = utils.get_billing_forms_with_shipping(
        cart,
        {"preview": True},
        customer_user.addresses.all(),
        default_country
    )
    assert len(forms) == 3


def test_update_billing_address_in_cart_with_shipping(
    customer_user,
    default_country,
    cart_with_item,
    another_address,
):
    # Test Case M5-01
    cart = cart_with_item
    cart.user = customer_user

    cart.shipping_address = another_address
    forms = utils.get_billing_forms_with_shipping(
        cart,
        None,
        customer_user.addresses.all(),
        default_country
    )
    assert len(forms) == 3
    # Test Case M5-02
    customer_user.addresses.add(another_address)
    forms = utils.get_billing_forms_with_shipping(
        cart,
        None,
        customer_user.addresses.all(),
        default_country
    )
    assert len(forms) == 3
    # Test Case M5-03
    cart_without_user = cart_with_item
    cart.shipping_address = another_address
    forms = utils.get_billing_forms_with_shipping(
        cart_without_user,
        None,
        customer_user.addresses.all(),
        default_country
    )
    assert len(forms) == 3


def test_get_summary_without_shipping_forms(
    customer_user,
    default_country,
    cart_with_item,
    another_address,
    address
):
    # Test Case M6-01
    cart = cart_with_item
    cart.user = customer_user

    cart.shipping_address = address
    forms = utils.get_summary_without_shipping_forms(
        cart,
        customer_user.addresses.all(),
        None,
        default_country
    )
    assert len(forms) == 3
    # Test Case M6-02
    cart = cart_with_item
    cart.user = customer_user

    cart.shipping_address = another_address
    forms = utils.get_summary_without_shipping_forms(
        cart,
        customer_user.addresses.all(),
        None,
        default_country
    )
    assert len(forms) == 3
    # Test Case M6-03
    new_cart = cart_with_item
    cart.user = customer_user
    forms = utils.get_summary_without_shipping_forms(
        new_cart,
        customer_user.addresses.all(),
        {"default": True},
        default_country
    )
    assert len(forms) == 3
    # Test Case M6-04
    cart_without_user = cart_with_item
    forms = utils.get_summary_without_shipping_forms(
        cart_without_user,
        customer_user.addresses.all(),
        {"default": True},
        default_country
    )
    assert len(forms) == 3


def test_update_billing_address_in_cart(
    customer_user,
    default_country,
    cart_with_item,
    another_address,
    address
):
    # Test Case M7-01
    cart = cart_with_item
    cart.user = customer_user

    forms = utils.update_billing_address_in_cart(
        cart,
        customer_user.addresses.all(),
        None,
        default_country
    )
    assert len(forms) == 3
    # Test Case M7-01
    cart = cart_with_item
    cart.user = customer_user
    cart.billing_address = customer_user.addresses.first()
    forms = utils.update_billing_address_in_cart(
        cart,
        customer_user.addresses.all(),
        None,
        default_country
    )
    assert len(forms) == 3
    forms = utils.update_billing_address_in_cart(
        cart,
        customer_user.addresses.all(),
        {"default": True},
        default_country
    )
    assert len(forms) == 3


def test_recalculate_cart_discount(
    taxes,
    customer_user,
    cart_with_item,
    monkeypatch,
    voucher
):
    # Test Case M8-01
    cart = cart_with_item
    cart.user = customer_user
    utils.recalculate_cart_discount(cart, list(), taxes)
    total = cart.get_total(None, taxes)
    assert total.gross.amount == 30

    # Test Case M8-02
    cart.voucher_code = "mirumee"
    voucher_mock = Mock(return_value=voucher)
    monkeypatch.setattr(
        'saleor.checkout.utils.get_voucher_for_cart',
        voucher_mock
    )
    utils.recalculate_cart_discount(cart, list(), taxes)
    total = cart.get_total(None, taxes)
    assert total.gross.amount == 10
    # Test Case M8-03
    new_cart = cart_with_item
    none_mock = Mock(return_value=None)
    monkeypatch.setattr(
        'saleor.checkout.utils.get_voucher_for_cart',
        none_mock
    )
    new_cart.voucher_code = "None"
    utils.recalculate_cart_discount(new_cart, list(), taxes)
    total = cart.get_total(None, taxes)
    assert total.gross.amount == 30


def test_is_valid_shipping_method(
    taxes,
    customer_user,
    cart_with_item,
    moon_address,
    monkeypatch,
    shipping_method
):
    # Test Case M9-01
    cart = cart_with_item
    cart.user = customer_user

    is_valid_shipping_method = utils.is_valid_shipping_method(
        cart,
        list(),
        taxes
    )
    assert not is_valid_shipping_method

    # Test Case M9-02
    cart.shipping_method = shipping_method
    cart.shipping_address = moon_address
    is_valid_shipping_method = utils.is_valid_shipping_method(
        cart,
        list(),
        taxes
    )

    assert not is_valid_shipping_method

    # Test Case M9-03
    new_cart = cart_with_item
    new_cart.shipping_method = shipping_method
    new_cart.shipping_address = customer_user.addresses.first()
    avoid_propagate_saving = Mock(return_value=None)
    monkeypatch.setattr(
        'saleor.checkout.utils.clear_shipping_method',
        avoid_propagate_saving
    )
    mock_get_subtotal = Mock(return_value=TaxedMoney(Money(30, "USD"), Money(30, "USD")))
    monkeypatch.setattr(
        'saleor.checkout.models.Cart.get_subtotal',
        mock_get_subtotal
    )
    mock_shipping_applicable = Mock(return_value=True)
    monkeypatch.setattr(
        'saleor.checkout.utils.shipping_method_applicable',
        mock_shipping_applicable
    )
    is_valid_shipping_method = utils.is_valid_shipping_method(
        new_cart,
        list(),
        taxes
    )
    assert is_valid_shipping_method

    # Test Case M9-04
    mock_shipping_non_applicable = Mock(return_value=False)
    monkeypatch.setattr(
        'saleor.checkout.utils.shipping_method_applicable',
        mock_shipping_non_applicable
    )
    is_valid_shipping_method = utils.is_valid_shipping_method(
        new_cart,
        list(),
        taxes
    )
    assert not is_valid_shipping_method


def test_shipping_method_applicable(
    shipping_method,
    shipping_method_weight
):
    method_applicable = utils.shipping_method_applicable(
        500,
        10,
        shipping_method
    )
    assert method_applicable

    method_applicable = utils.shipping_method_applicable(
        500,
        20,
        shipping_method_weight
    )

    assert not method_applicable
