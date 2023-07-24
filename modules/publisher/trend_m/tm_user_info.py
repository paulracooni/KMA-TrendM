from cryptography.fernet import Fernet

class TMUserInfo:

    def __init__(self, email, password):
        
        self.__encryptor = Fernet(Fernet.generate_key())
        self.__email = self.__encrypt(email)
        self.__password = self.__encrypt(password)

    def __str__(self) -> str:
        return f"TMUserInfo(email={self.__email}, password={self.__password})"
    @property
    def email(self):
        return self.__decrypt(self.__email)
    
    @email.setter
    def email(self, value):
        self.__email = self.__encrypt(value)

    @property
    def password(self):
        return self.__decrypt(self.__password)
    
    @password.setter
    def password(self, value):
        self.__password = self.__encrypt(value)

    def __encrypt(self, text):
        return self.__encryptor.encrypt(text.encode())
    
    def __decrypt(self, text):
        return self.__encryptor.decrypt(text).decode()