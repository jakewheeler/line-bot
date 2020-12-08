import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("creds.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


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


def pay_user(sender_id, receiver_name, value):
    sender_ref = get_user(sender_id)
    receiver_ref = get_user_by_name(receiver_name)

    sender_data = sender_ref.to_dict()
    receiver_data = receiver_ref.to_dict()

    if int(sender_data["money"]) < value:
        return "Cannot process transaction. You too broke."

    sender_data["money"] = int(sender_data["money"]) - int(value)
    receiver_data["money"] = int(receiver_data["money"]) - int(value)

    db.collection("users").document(sender_ref.id).set(sender_data)
    db.collection("users").document(receiver_ref.id).set(receiver_data)
    return "Transaction complete!"


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


get_user_by_name("test")

