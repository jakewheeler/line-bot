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
    return f"Thanks for creating an account with Lancaster Community Bank. {account_creation_bonus} DB (Dosh Bucks) have been added to your account for signing up."


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

    return f"You have received {payout_value} DB. Spend it wisely."


def __parse_chat_message(msg):
    split = msg.split(" ")
    return {"cmd": split[0], "args": split[1:]}


def __fetch_all_members(id):
    if id == "":
        return "User must exist."

    list_str = f""
    users = db.collection("users").stream()
    for user in users:
        list_str += user.get("name") + "\n"
    return list_str[:-1]


def __check_balance(id):
    user_snap = db.collection("users").document(id).get()
    if user_snap == None:
        return "User does not exist."
    return f"You have {user_snap.get('money')} DB in your account."


def __bank_help(id):
    if id == "":
        return "User must exist."
    help_text = f""
    for v in payment_cmd.values():
        help_text += v["fmt"] + ": " + v["help_msg"] + "\n"
    return help_text[:-1]  # remove \n from the end


#### API ####


def handler(line_id, chat_message):
    parsed = __parse_chat_message(chat_message)
    user_cmd = parsed["cmd"]
    args = parsed["args"]
    if user_cmd in payment_cmd:
        try:
            return True, payment_cmd[user_cmd]["action"](line_id, *args)
        except:
            return False, ""


def collect_ubi(line_id):
    # user can collect money once per day
    return __payout(line_id)


def bank_help(line_id):
    return __bank_help(line_id)


def register(line_id, name):
    if name == "":
        return "Name is required."

    status = _register_user(line_id, name)
    return status


def get_members(line_id):
    return __fetch_all_members(line_id)


def check_balance(line_id):
    return __check_balance(line_id)


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


payment_cmd = {
    "!register": {
        "action": register,
        "fmt": "!register [username]",
        "help_msg": "Register an account with Lancaster Community Bank.",
    },
    "!members": {
        "action": get_members,
        "fmt": "!members",
        "help_msg": "List members of LCB.",
    },
    "!ubi": {
        "action": collect_ubi,
        "fmt": "!ubi",
        "help_msg": "Collect your UBI. You can do this once per day.",
    },
    "!balance": {
        "action": check_balance,
        "fmt": "!balance",
        "help_msg": "Check your account balance.",
    },
    "!pay": {
        "action": pay_user,
        "fmt": "!pay [username] [amount]",
        "help_msg": "Pay another LCB member.",
    },
    "!bankhelp": {
        "action": bank_help,
        "fmt": "!bankhelp",
        "help_msg": "List all available bank commands.",
    },
}

# print(pay_user("id3", "william", 1))
# register("id4", "william")
# print(collect_ubi("id4"))
print(handler("id5", "!bankhelp")[1])
# handler("idk", "!test my command")

