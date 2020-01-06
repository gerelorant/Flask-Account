from warnings import warn

from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy

from flask_account.model import \
    UserMixin, RoleMixin, IdentifierMixin, set_secret_key


class Account:
    def __init__(
            self,
            app: Flask = None,
            db: SQLAlchemy = None,
            user_model: type(UserMixin) = None,
            role_model: type(RoleMixin) = None,
            identifier_model: type(IdentifierMixin) = None
    ):
        self.app = app
        self.db = db
        self.security = None

        self.user_class = user_model
        self.role_class = role_model
        self.identifier_class = identifier_model

        self.admin_role = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        app.extensions['account'] = self

        self.admin_role = app.config.get('ACCOUNT_ADMIN_ROLE', 'admin')
        set_secret_key(app.config.get('SECRET_KEY', 'secret'))

        if self.role_class is None:
            class Role(self.db.Model, RoleMixin):
                pass

            self.role_class = Role

        if self.user_class is None:
            class User(self.db.Model, UserMixin):
                roles = self.db.relationship(
                        'Role',
                        secondary=self.db.Table(
                            "user_role",
                            self.db.Column(
                                'user_id',
                                self.db.Integer,
                                self.db.ForeignKey('user.id'),
                                primary_key=True
                            ),
                            self.db.Column(
                                'role_id',
                                self.db.Integer,
                                self.db.ForeignKey('role.id'),
                                primary_key=True
                            )
                        ),
                        backref=self.db.backref('users', lazy='dynamic'),
                        lazy='dynamic'
                    )

            self.user_class = User

        if self.identifier_class is None:
            class Identifier(self.db.Model, IdentifierMixin):
                pass

            self.identifier_class = Identifier

        self.security = Security(
            self.app,
            SQLAlchemyUserDatastore(
                self.db,
                self.user_class,
                self.role_class
            )
        )
        try:
            if self.role_class.query\
                    .filter_by(name=self.admin_role)\
                    .first() is None:
                admin = self.role_class()
                admin.name = self.admin_role
                self.db.session.add(admin)
                self.db.session.commit()
        except Exception as e:
            warn("Could not check if 'admin' role exists.")
            warn(e)

    def get_user(self, identity: str):
        attributes = self.app.config.get('SECURITY_USER_IDENTITY_ATTRIBUTES')
        args = [getattr(self.user_class, col) for col in attributes]
        users = self.db.session.query(self.user_class.id, *args).all()
        for user in users:
            if identity in user:
                return self.user_class.query.get(user.id)
