import os
import secrets
import string
import pytz
import datetime
import requests
from cryptography.fernet import Fernet


class TeleDjanAuth:
    """
    Using of this library implies that you have django server, some API and you need to
    create new user for login to API with telegram
    Its implies that your telegram users have some unique data
    AND maybe you will need to use this telegram-user data for login to web version of your api

    """
    key = None

    def __init__(self, relations_table, url_login, url_new_user, crypto_key,
                 ):
        self.relations_table = relations_table
        self.url_login = url_login
        self.url_new_user = url_new_user
        self.key = crypto_key

    def _login(self, username, password):
        """

        :return token
        """
        response = requests.post(self.url_login, data={'username': username,
                                                       'password': password})
        if response.status_code != 200:
            return {'error': {'login': f'status code {response.status_code}'}}
        token = response.json().get('auth_token')
        if token is None:
            return {'error': {'login': 'no token in response'}}
        return token

    def _login_by_id(self, user_id):
        username = self._get_username_from_relations_table(user_id)
        password = self._get_password_from_relations_table(user_id)
        return self._login(username, password)

    def _update_token_in_relations_table(self, user_id, token):
        """
        Update token for user using django ORM
        :param user_id:
        :param token:
        :return:
        """
        try:
            token = self._encrypt(token)
            relation = self.relations_table.objects.get(user_id=user_id)
            relation.token = token
            relation.save(update_fields=['token'])
        except self.relations_table.DoesNotExist:
            return {'error': 'TelegramUserToPasswordRelation object does not exist'}
        except self.relations_table.MultipleObjectsReturned:
            return {'error': 'TelegramUserToPasswordRelation multiple object returned'}

    def _get_password_from_relations_table(self, user_id):
        """
        Get token for user using django ORM
        """
        try:
            relation = self.relations_table.objects.get(user_id=user_id)
            return self._decrypt(relation.password)
        except self.relations_table.DoesNotExist:
            return {'error': f'Try get object from relations table: object {user_id} does not exist'}
        except self.relations_table.MultipleObjectsReturned:
            return {'error': f'Try get object from relations table: multiple objects {user_id} returned'}

    def _get_token_from_relations_table(self, user_id):
        """
        Get token for user using django ORM
        """
        try:
            relation = self.relations_table.objects.get(user_id=user_id)
            return self._decrypt(relation.token)
        except self.relations_table.DoesNotExist:
            return {'error': f'Try get object from relations table: object {user_id} does not exist'}
        except self.relations_table.MultipleObjectsReturned:
            return {'error': f'Try get object from relations table: multiple objects {user_id} returned'}

    def _get_username_from_relations_table(self, user_id):
        """
        Get token for user using django ORM
        """
        try:
            relation = self.relations_table.objects.get(user_id=user_id)
            return relation.username
        except self.relations_table.DoesNotExist:
            return {'error': f'Try get object from relations table: object {user_id} does not exist'}
        except self.relations_table.MultipleObjectsReturned:
            return {'error': f'Try get object from relations table: multiple objects {user_id} returned'}

    def _get_credentials_from_relations_table(self, user_id):
        """
        Get token for user using django ORM
        """
        try:
            relation = self.relations_table.objects.get(user_id=user_id)
            password = self._decrypt(relation.password)
            return {'username': relation.username, 'password': password}
        except self.relations_table.DoesNotExist:
            return {'error': f'Try get object from relations table: object {user_id} does not exist'}
        except self.relations_table.MultipleObjectsReturned:
            return {'error': f'Try get object from relations table: multiple objects {user_id} returned'}

    def _create_user(self, username, password):
        response = requests.post(self.url_new_user, data={'username': username,
                                                          'password': password})
        if response.status_code != 201:
            return {'error': f'error while creating new user, status code = {response.status_code}'}

    def _encrypt(self, message_to_encrypt: str) -> str:
        crypto = Fernet(self.key.encode())
        encrypted_message = crypto.encrypt(message_to_encrypt.encode())
        return encrypted_message.decode()

    def _decrypt(self, message_to_decrypt):
        decrypto = Fernet(self.key.encode())
        decrypted_message = decrypto.decrypt(message_to_decrypt.encode())
        return decrypted_message.decode()

    @staticmethod
    def generate_password() -> str:
        alphabet = string.ascii_letters + string.digits
        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(10))
            if (any(c.islower() for c in password)
                    and any(c.isupper() for c in password)
                    and sum(c.isdigit() for c in password) >= 3):
                break
        return password

    def authenticate_by_telegram(self, user_id: dict) -> str:
        """
        Login to API
        Args:
            user_id: telegram_id of user
        Returns:
            token
        """
        username = str(user_id)
        current_user = self.relations_table.objects.filter(user_id=user_id)
        if not current_user:
            new_password = self.generate_password()
            encrypted_password = self._encrypt(new_password)
            result = self._create_user(username, new_password)
            if result and 'error' in result:
                return f'error {result["error"]}'
            token = self._login(username, new_password)
            if result and 'error' in result:
                return f'error {token["error"]}'
            encrypted_token = self._encrypt(token)

            last_update=datetime.datetime.now(tz=pytz.UTC).isoformat()
            self.relations_table.objects.create(user_id=user_id, password=encrypted_password,
                                                username=username, token=encrypted_token, last_update=last_update)
            return token
        token = self._login_by_id(user_id)
        if isinstance(token, dict) and token.get('error'):
            return f'error {token["error"]}'
        result = self._update_token_in_relations_table(user_id, token)
        if isinstance(result, dict) and result.get('error'):
            return f'error {result["error"]}'
        return token
