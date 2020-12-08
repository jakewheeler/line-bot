import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("creds.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


def get_collection_ref(name):
    return db.collection(name)


def register_user(id, name):
    if get_user(id) != None:
        print(f"User has already registered: {id}")
        return "User already exists in the database"

    # register user and pay them!
    user = {"money": 100, "name": name, "receivedPayments": [], "sentPayments": []}
    db.collection("users").document(id).set(user)
    print(f"Successfully registered user ID {id}")
    return (
        "Thanks for registering at Lancaster Bank. $100 has been added to your account."
    )


@firestore.transactional
def pay_user(transaction, sender, receiver, value):
    send_snap = sender.get(transaction=transaction)
    rec_snap = receiver.get(transaction=transaction)
    # check if user has cash
    if send_snap.get("money") < value:
        print("Sender does not have enough money to pay receiver.")
        return False

    transaction.update(
        sender,
        {
            "money": send_snap.get("money") - value,
            "sentPayments": firestore.ArrayUnion(
                [{"to": rec_snap.get("name"), "value": value}]
            ),
        },
    )
    transaction.update(
        receiver,
        {
            "money": rec_snap.get("money") + value,
            "receivedPayments": firestore.ArrayUnion(
                [{"from": send_snap.get("name"), "value": value}]
            ),
        },
    )

    return True


def get_user(id):
    doc_ref = db.collection("users").document(id)

    doc = doc_ref.get()
    if doc.exists:
        return doc
    else:
        return None


def get_user_by_name(name):
    user = db.collection("users").where("name", "==", name).get()[0]
    return user


sender_ref = db.collection("users").document("myid")
receiver_ref = db.collection("users").document("idk")
transaction = db.transaction()
print(pay_user(transaction, sender_ref, receiver_ref, 24))

# register_user("myid", "jake")

