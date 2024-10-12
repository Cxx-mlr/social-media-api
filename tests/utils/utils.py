from faker import Faker

fake = Faker()

def random_email():
    return fake.email()

def random_password():
    return fake.password(length=8)

def random_title():
    return fake.sentence(3)

def random_content():
    return fake.sentence(13)