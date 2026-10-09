from tools import get_order_status


def test_existing_order():
    result = get_order_status("KE1002")
    assert "Shipped" in result


def test_lowercase_order_id():
    result = get_order_status("ke1005")
    assert "Processing" in result


def test_unknown_order():
    result = get_order_status("KE9999")
    assert "No order found" in result