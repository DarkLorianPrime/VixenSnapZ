class Responses:
    NOT_VALID_CYRILLIC_OR_LENGTH = "Password must be longer than 8 characters and contain only english symbols and nums"
    ACCOUNT_EXISTS = "Account with this username or email already exists"
    LOGIN_OR_PASSWORD_NF = "Account with this login or password not exists"
    USERNAME_NOT_VALID = "Username not valid. Valid scheme: /^[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*$/"
    EMAIL_NOT_VALID = "Email not valid. Valid scheme: /^\S+@\S+\.\S+$/"
    NOT_EMAIL_NOT_USERNAME = "Email or username was not shared"
