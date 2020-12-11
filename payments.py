import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime as dt
import pytz

cred = credentials.Certificate("creds.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
transaction = db.transaction()


def _register_user(id, name):
    account_creation_bonus = 100
    # check if user is already registered
    if _get_user(id) != None:
        return "This LINE account has already registered."

    # check if username is taken
    if _get_user_by_name(name) != None:
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
    return f"Thanks for registering at Lancaster Bank. {account_creation_bonus} Dosh Bucks have been added to your account."


@firestore.transactional
def _pay_user(transaction, sender, receiver, value):
    send_snap = sender.get(transaction=transaction)
    rec_snap = receiver.get(transaction=transaction)

    if send_snap == None or rec_snap == None:
        return "Invalid sender or receiver."

    # check that sender and receiver are different users
    if sender.id == receiver.id:
        return "You can't send money to yourself.."

    # check if user has cash
    if send_snap.get("money") < value:
        return f"{send_snap.get('name')} does not have enough DB to pay {rec_snap.get('name')}."

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

    return f"{send_snap.get('name')} successfully sent {value} DB to {rec_snap.get('name')}."


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


def __user_has_been_paid_on_date(user_ref, date):
    snap = user_ref.get()
    payouts = snap.get("payouts")

    if payouts.get(date) == None:
        return False
    return True


def __payout(line_id):
    payout_value = 20
    todays_date = dt.now(tz=pytz.timezone("US/Eastern")).strftime("%Y-%m-%d")

    # get user from id
    user = _get_user(line_id)

    if user == None:
        return "ID is not valid."

    user_ref = db.collection("users").document(line_id)

    if __user_has_been_paid_on_date(user_ref, todays_date):
        return "You have already been paid out today."

    user_snap = user_ref.get()
    # create the payment
    user_ref.update(
        {
            "money": user_snap.get("money") + payout_value,
            f"payouts.{todays_date}": True,
        }
    )

    return f"You have received {payout_value} Dosh Bucks."


def __parse_chat_message(msg):
    split = msg.split(" ")
    return {"cmd": split[0], "args": split[1:]}


#### API ####


def handler(line_id, chat_message):
    parsed = __parse_chat_message(chat_message)
    user_cmd = parsed["cmd"]
    args = parsed["args"]
    if user_cmd in available_commands:
        try:
            return True, available_commands[user_cmd]["action"](line_id, *args)
        except:
            return False, ""


def collect_ubi(line_id):
    # user can collect money once per day
    return __payout(line_id)


def register(line_id, name):
    if name == "":
        return "Name is required."

    status = _register_user(line_id, name)
    return status


def pay_user(sender_id, receiver_name, value):
    try:
        value = int(value)
        sender_ref = db.collection("users").document(sender_id)
        receiver_ref = db.collection("users").document(
            _get_user_by_name(receiver_name).id
        )
        return _pay_user(transaction, sender_ref, receiver_ref, value)
    except:
        return "Invalid sender or receiver."


available_commands = {
    "!register": {"action": register},
    "!ubi": {"action": collect_ubi},
    "!pay": {"action": pay_user},
}

# print(pay_user("id3", "william", 1))
# register("id4", "william")
# print(collect_ubi("id4"))
print(handler("id5", "!pay william 26"))
# handler("idk", "!test my command")

