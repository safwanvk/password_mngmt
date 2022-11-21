from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

# Extended User
class User(AbstractUser):
    options = (
        ('Active','Active'),
        ('For Approval','For Approval'),
        ('Pending Verification','Pending Verification')
    )
    username = None
    email = models.EmailField(_('email address'), unique=True)  
    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updatedAt = models.DateTimeField(auto_now=True)
    organizations = models.ManyToManyField('Organization', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    @property
    def passwords(self):
        organizations = Organization.objects.values_list('id', flat=True).filter(user=self)
        passwords = Password.objects.filter(organization_passwords__in=organizations).values_list('id', flat=True)
        return passwords


class Password(models.Model):
    title = models.CharField(max_length=128, unique=True)
    password = models.CharField(_("password"), max_length=128)
    date = models.DateTimeField(auto_now_add=True)
    duration_in_days = models.IntegerField()
    expired_at = models.DateTimeField(blank=True, null=True)

# Organization Model
class Organization(models.Model):
    name = models.CharField(max_length=50, verbose_name='Name', null=True)
    organizationId = models.CharField(max_length=10, unique=True, verbose_name='Organization id', null=True)
    organizationSize = models.CharField(max_length=15, verbose_name='Organization Size', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    passwords = models.ManyToManyField(Password, blank=True, related_name='organization_passwords')

    def __str__(self):
        return self.name
