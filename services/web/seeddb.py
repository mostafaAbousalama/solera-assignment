from project import app, db, User, Admin

import bcrypt

users_sample = [
    {
        'name':'Khaled',
        'email':'khaled@solera.com',
        'plaintext_password':'khaledPass',
        'reading':100,
        'balance':50
    },
    {
        'name':'Mohamed',
        'email':'mohamed@solera.com',
        'plaintext_password':'mohamedPass',
        'reading':150,
        'balance':75
    },
    {
        'name':'Karim',
        'email':'karim@solera.com',
        'plaintext_password':'karimPass',
        'reading':200,
        'balance':100
    },
    {
        'name':'Rania',
        'email':'rania@solera.com',
        'plaintext_password':'raniaPass',
        'reading':300,
        'balance':150
    },
    {
        'name':'Mark',
        'email':'mark@solera.com',
        'plaintext_password':'markPass',
        'reading':100,
        'balance':50
    },
    {
        'name':'Moustafa',
        'email':'moustafa@solera.com',
        'plaintext_password':'moustafaPass',
        'reading':60,
        'balance':35
    },
    {
        'name':'Youssef',
        'email':'youssef@solera.com',
        'plaintext_password':'youssefPass',
        'reading':120,
        'balance':60
    },
    {
        'name':'Ibrahim',
        'email':'ibrahim@solera.com',
        'plaintext_password':'ibrahimPass',
        'reading':10,
        'balance':5
    },
    {
        'name':'Kamal',
        'email':'kamal@solera.com',
        'plaintext_password':'kamalPass',
        'reading':1000,
        'balance':500
    },
    {
        'name':'Shady',
        'email':'shady@solera.com',
        'plaintext_password':'shadyPass',
        'reading':110,
        'balance':55
    }
]

admins_sample = [
    {
        'username':'Admin1',
        'plaintext_password':'Admin1Pass'
    },
    {
        'username':'Admin2',
        'plaintext_password':'Admin2Pass'
    }
]

def seed_db():
    for user_dict in users_sample:
        salt = bcrypt.gensalt(13)
        plain_pass = user_dict.get('plaintext_password')
        b_pass = plain_pass.encode('utf-8')
        hashed_pass = bcrypt.hashpw(b_pass, salt)
        hash_pass_decoded = hashed_pass.decode('utf-8')
        new_user = User(name=user_dict.get('name'), email=user_dict.get('email'), hashed_password=hash_pass_decoded, current_balance=user_dict.get('balance'), current_reading=user_dict.get('reading'))
        db.session.add(new_user)
        db.session.commit()

    for admin_dict in admins_sample:
        salt = bcrypt.gensalt(13)
        plain_pass = admin_dict.get('plaintext_password')
        b_pass = plain_pass.encode('utf-8')
        hashed_pass = bcrypt.hashpw(b_pass, salt)
        hash_pass_decoded = hashed_pass.decode('utf-8')
        new_admin = Admin(username=admin_dict.get('username'), hashed_password=hash_pass_decoded)
        db.session.add(new_admin)
        db.session.commit()

seed_db()
