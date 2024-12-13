import bcrypt

def hashPassword(plainPassword: str):
    encodedPassword = plainPassword.encode("utf-8")
    hashedPassword = bcrypt.hashpw(
        password=encodedPassword, salt=bcrypt.gensalt(rounds=10)
    )
    return hashedPassword

def comparePassword(userInput: str,hashedPassword: str):
    return bcrypt.checkpw(password=userInput.encode("utf-8"), hashed_password= hashedPassword.encode("utf-8"))
