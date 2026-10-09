import csv
import os


ORDERS_FILE = os.path.join("data", "orders.csv")


def get_order_status(order_id: str) -> str:
    """
    Look up a KartEase order by order ID.

    The search is case-insensitive.
    """

    order_id = order_id.strip().upper()

    if not os.path.exists(ORDERS_FILE):
        return "Orders file not found."

    with open(ORDERS_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:

            current_order_id = row["order_id"].strip().upper()

            if current_order_id == order_id:

                return (
                    f"Order ID: {row['order_id']}\n"
                    f"Customer: {row['customer_name']}\n"
                    f"Product: {row['product']}\n"
                    f"Category: {row['category']}\n"
                    f"Order Date: {row['order_date']}\n"
                    f"Status: {row['status']}\n"
                    f"Expected/Delivered Date: "
                    f"{row['expected_or_delivered_date']}\n"
                    f"Amount: ₹{row['amount_inr']}\n"
                    f"Payment Method: {row['payment_method']}"
                )

    return f"No order found with ID {order_id}."


if __name__ == "__main__":

    print("=" * 60)
    print("Testing KE1002")
    print("=" * 60)
    print(get_order_status("KE1002"))

    print("\n" + "=" * 60)
    print("Testing ke1005")
    print("=" * 60)
    print(get_order_status("ke1005"))

    print("\n" + "=" * 60)
    print("Testing KE9999")
    print("=" * 60)
    print(get_order_status("KE9999"))