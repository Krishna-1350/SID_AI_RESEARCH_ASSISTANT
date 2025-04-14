from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import MinLengthValidator

# Create your models here.
class UserManager(BaseUserManager):
    """ Manager: User model """

    def create_user(self, email, password, **extra_fields):
        """ Create and save a new user """

        user = self.model(email=email.lower(), **extra_fields)
        # Set password with hash
        user.set_password(password)
        user.save(using=self._db)
        return user

    
class User(AbstractBaseUser, PermissionsMixin):
    """ Model: User """

    # Field declarations
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(validators=[MinLengthValidator(10)], max_length=10, blank=True, null=True, unique=True)
    date_of_birth = models.DateField()

    # Additional field declarations
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True) 
    
    # Set Django defaults
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    # Reference custom manager
    objects = UserManager()

    # Unique identifier field
    USERNAME_FIELD = 'email'
    
    # String representation of model
    def __str__(self):
        return self.email