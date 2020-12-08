import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime as dt
import pytz

cred = credentials.Certificate("creds.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


def _register_user(id, name):
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


#### API ####


def register(line_id, name):
    status = _register_user(line_id, name)
    return status


def pay(sender_id, receiver_name, value):
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


pay("idk2", "jake", 12)

