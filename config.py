import os

# Koyeb-এর Environment Variables থেকে ডেটা নেবে
# যদি সেখানে না পায়, তবে দ্বিতীয় প্যারামিটার (আসল আইডি) ব্যবহার করবে
api_id = int(os.environ.get("API_ID", 24670806))
api_hash = os.environ.get("API_HASH", "82134723a32b2cae76b9cfb3b1570745")
bot_token = os.environ.get("BOT_TOKEN", "8367209194:AAG9KjF5v5ti8KCedqqiX1sVl1PlOed30c4")

auth_users = [8229228616]
sudo_users = [8229228616]
