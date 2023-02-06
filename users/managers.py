from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_accepted_terms_of_offer, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')

        if not is_accepted_terms_of_offer:
            raise ValueError('Вы должны согласиться с условиями Оферты')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_accepted_terms_of_offer=is_accepted_terms_of_offer,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, is_accepted_terms_of_offer, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, is_accepted_terms_of_offer, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
