from django.db.models import EmailField, CharField, DateTimeField, BooleanField, IntegerField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.



class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password, **other_fields):
        
        # Field validation
        if not email:
            raise ValueError("The user must have an email.")
        if not username:
            raise ValueError("The user must have a username.")
        
        # Let's create the user

        user = self.model(email=self.normalize_email(email), username=username, **other_fields)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **other_fields):

        # Field validation
        if not email:
            raise ValueError("The user must have an email.")
        if not username:
            raise ValueError("The user must have a username.")
        
        # Let's create the super_user

        user = self.create_user(email=self.normalize_email(email), username=username, password=password, **other_fields)

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)

        user.save()
        return user



class Interpreter(AbstractBaseUser, PermissionsMixin):

    #Campor requeridos

    email = EmailField(verbose_name="email", max_length=150, unique=True, blank=True)
    username = CharField(verbose_name="username", max_length=100, unique=True, blank=True)
    date_joined = DateTimeField(verbose_name="date joined", auto_now=True)
    last_login = DateTimeField(verbose_name="last login", auto_now_add=True)
    is_admin = BooleanField(verbose_name="Is admin", default=False)
    is_active = BooleanField(verbose_name="Is active", default=True)
    is_staff = BooleanField(verbose_name="Is staff", default=False)
    is_superuser = BooleanField(verbose_name="Is superuser", default=False)

    #Campos Opcionales

    phone = IntegerField(verbose_name="Phone Number", blank=True, null=True)

    #The field to log in

    USERNAME_FIELD = "email"

    # These are mandatory fields when creating an interpreter

    REQUIRED_FIELDS = [
        "username",
    ]

    objects = MyUserManager()

    # Dunder methods to show the user
    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True









