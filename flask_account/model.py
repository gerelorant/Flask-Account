import typing

from flask import current_app
import flask_security as fs
from flask_sqlalchemy import Model
import sqlalchemy as sa
from sqlalchemy_utils.types.encrypted.encrypted_type import \
    EncryptedType, AesEngine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref


secret_key = ''


def set_secret_key(key: str):
    global secret_key
    secret_key = key


class RoleMixin(Model, fs.RoleMixin):
    name = sa.Column(sa.String(40), unique=True, nullable=True, index=True)


class UserMixin(Model, fs.UserMixin):
    username = sa.Column(sa.String(16), unique=True, nullable=True, index=True)
    password = sa.Column(sa.String(255))
    active = sa.Column(sa.Boolean, default=True)

    # noinspection PyMethodParameters
    @declared_attr
    def email(cls):
        return sa.Column(
            EncryptedType(
                sa.String(255),
                key=secret_key,
                engine=AesEngine,
                padding='pkcs5'
            ),
            unique=True
        )

    # noinspection PyMethodParameters
    @declared_attr
    def country(cls):
        return sa.Column(
            EncryptedType(
                sa.String(2),
                key=secret_key,
                engine=AesEngine,
                padding='pkcs5'
            ),
            unique=True
        )

    # noinspection PyMethodParameters
    @declared_attr
    def zip(cls):
        return sa.Column(
            EncryptedType(
                sa.String(255),
                key=secret_key,
                engine=AesEngine,
                padding='pkcs5'
            ),
            unique=True
        )

    # noinspection PyMethodParameters
    @declared_attr
    def state(cls):
        return sa.Column(
            EncryptedType(
                sa.String(40),
                key=secret_key,
                engine=AesEngine,
                padding='pkcs5'
            ),
            unique=True
        )

    # noinspection PyMethodParameters
    @declared_attr
    def city(cls):
        return sa.Column(
            EncryptedType(
                sa.String(80),
                key=secret_key,
                engine=AesEngine,
                padding='pkcs5'
            ),
            unique=True
        )

    # noinspection PyMethodParameters
    @declared_attr
    def address(cls):
        return sa.Column(
            EncryptedType(
                sa.String(120),
                key=secret_key,
                engine=AesEngine,
                padding='pkcs5'
            ),
            unique=True
        )

    # noinspection PyMethodParameters
    @declared_attr
    def address2(cls):
        return sa.Column(
            EncryptedType(
                sa.String(120),
                key=secret_key,
                engine=AesEngine,
                padding='pkcs5'
            ),
            unique=True
        )

    # noinspection PyMethodParameters
    @declared_attr
    def phone(cls):
        return sa.Column(
            EncryptedType(
                sa.String(120),
                key=secret_key,
                engine=AesEngine,
                padding='pkcs5'
            ),
            unique=True
        )

    def has_any_role(self, *roles: typing.Union[str, RoleMixin]):
        if self.has_role(current_app.extensions['account'].admin_role):
            return True

        for role in roles:
            if self.has_role(role):
                return True

        return False

    def has_all_roles(self, *roles: typing.Union[str, RoleMixin]):
        if self.has_role(current_app.extensions['account'].admin_role):
            return True

        for role in roles:
            if not self.has_role(role):
                return False

        return True


class IdentifierMixin(Model):
    code = sa.Column(sa.String(16), nullable=False, unique=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), index=True)
    user = relationship(
        'User',
        backref=backref('identifiers', lazy='dynamic'),
        lazy='dynamic'
    )
