# echo/hashers.py
from django.contrib.auth.hashers import BasePasswordHasher
from hashlib import sha256
import secrets

class CustomHasher(BasePasswordHasher):
    algorithm = "custom_sha256"  # Уникальное имя алгоритма

    def salt(self):
        # Генерируем случайную "соль" (16 символов)
        return secrets.token_hex(8)

    def encode(self, password, salt):
        # Хешируем пароль: SHA512(соль + пароль)
        hash = sha256((salt + password).encode('utf-8')).hexdigest()
        return f"{self.algorithm}${salt}${hash}"

    def verify(self, password, encoded):
        # Проверяем пароль
        algorithm, salt, hash = encoded.split('$', 2)
        new_hash = sha256((salt + password).encode('utf-8')).hexdigest()
        return secrets.compare_digest(hash, new_hash)

    def safe_summary(self, encoded):
        # Для админки
        algorithm, salt, hash = encoded.split('$', 2)
        return {
            'algorithm': algorithm,
            'salt': salt,
            'hash': hash[:10] + '...'  # Частичный показ
        }