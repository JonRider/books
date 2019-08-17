from passlib.apps import custom_app_context as pwd_context

def main():
    raw_pass = input("Enter Password: ")
    hash = hash_pass(raw_pass)
    print(f"Your encoded password is: {hash}")
    new_pass = input("Verify Password: ")
    correct_pass = verify_hash(new_pass, hash)
    print(f"The password you entered is {correct_pass}")

def hash_pass(raw_pass):
    return pwd_context.hash(raw_pass)

def verify_hash(raw_pass, hash):
    return pwd_context.verify(raw_pass, hash)

if __name__ == '__main__':
    main()
