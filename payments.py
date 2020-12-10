import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime as dt
import pytz

cred = credentials.Certificate("creds.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


def _register_user(id, name):

    # check if user is already registered
    if _get_user(id) != None:
        print(f"User has already registered: {id}")
        return "This LINE account has already registered."

    # check if username is taken
    if _get_user_by_name(name) != None:
        print("This username is taken")
        return "This username is taken."

    # register user and pay them!
    user = {
        "money": 100,
        "name": name,
        "receivedPayments": [],
        "sentPayments": [],
        "payouts": {},
        "createdAt": dt.now(tz=pytz.timezone("US/Eastern")),
    }

    db.collection("users").document(id).set(user)
    print(f"Successfully registered user ID {id}")
    return (
        "Thanks for registering at Lancaster Bank. $100 has been added to your account."
    )


@firestore.transactional
def _pay_user(transaction, sender, receiver, value):
    send_snap = sender.get(transaction=transaction)
    rec_snap = receiver.get(transaction=transaction)

    if send_snap == None or rec_snap == None:
        print("At least one user was invalid.")
        return False

    # check that sender and receiver are different users
    if sender.id == receiver.id:
        print("User can't send money to themselves.")
        return False

    # check if user has cash
    if send_snap.get("money") < value:
        print("Sender does not have enough money to pay receiver.")
        return False

    transaction.update(
        sender,
        {
            "money": send_snap.get("money") - value,
            "sentPayments": firestore.ArrayUnion(
                [
                    {
                        "to": rec_snap.get("name"),
                        "value": value,
                        "createdAt": dt.now(tz=pytz.timezone("US/Eastern")),
                    }
                ]
            ),
        },
    )
    transaction.update(
        receiver,
        {
            "money": rec_snap.get("money") + value,
            "receivedPayments": firestore.ArrayUnion(
                [
                    {
                        "from": send_snap.get("name"),
                        "value": value,
                        "createdAt": dt.now(tz=pytz.timezone("US/Eastern")),
                    }
                ]
            ),
        },
    )

    return True


def _get_user(id):
    doc_ref = db.collection("users").document(id)

    doc = doc_ref.get()
    if doc.exists:
        return doc
    else:
        return None


def _get_user_by_name(name):
    users = db.collection("users").where("name", "==", name).stream()
    for user in users:
        return user

    return None


def __user_has_been_paid_today(user_ref, date):
    snap = user_ref.get()
    payouts = snap.get("payouts")

    if payouts.get(date) == None:
        return False
    return True


def __payout(line_id):
    payout_value = 20
    todays_date = dt.now(tz=pytz.timezone("US/Eastern")).strftime("%Y-%m-%d")

    # get user from id
    user_ref = _get_user(line_id)

    if user_ref == None:
        return "ID is not valid."

    if __user_has_been_paid_today(user_ref, todays_date):
        return "You have already been paid out today."

    user_snap = user_ref.get()
    # create the payment
    user_ref.update(
        {
            "money": user_snap.get("money") + payout_value,
            f"payouts.{todays_date}": True,
        }
    )

    return "You have received some dough."


#### API ####


def pay_me(line_id):
    # user can collect money once per day
    return __payout(line_id)


def register(line_id, name):
    status = _register_user(line_id, name)
    return status


def pay_user(sender_id, receiver_name, value):
    try:
        sender_ref = db.collection("users").document(sender_id)
        receiver_ref = db.collection("users").document(
            _get_user_by_name(receiver_name).id
        )
        transaction = db.transaction()
        _pay_user(transaction, sender_ref, receiver_ref, value)

        return "Transaction was successful."
    except:
        return "Transaction could not complete."


# pay("exampleid", "hello", 1)
# print(__daily_payout("idk2"))
# register("id3", "bill")
print(__payout("id34"))

