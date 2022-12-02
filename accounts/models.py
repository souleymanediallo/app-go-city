from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save

import uuid


class MyUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone, condition, user_choices, password=None):
        if not email:
            raise ValueError('Votre adresse email est obligatoire !')

        user = self.model(
            user_choices=user_choices,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            condition=condition,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, phone, condition, user_choices, password=None):
        user = self.create_user(
            email,
            user_choices=user_choices,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            condition=condition,
        )
        user.is_admin = True
        user.is_staff = True

        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):

    USER_CHOICES = (
        ('Homme', 'Homme'),
        ('Femme', 'Femme')
    )
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=12)
    user_choices = models.CharField(max_length=50, choices=USER_CHOICES, default='PARTICULIER')
    condition = models.BooleanField(default=False)

    # required
    last_login = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['user_choices', 'first_name', 'last_name', 'phone', 'condition']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(default="user.png", upload_to="photos/%Y/%m", blank=True, null=True)
    description = models.TextField(max_length=300, blank=True, null=True)
    instagram = models.URLField(max_length=400, blank=True, null=True)
    facebook = models.URLField(max_length=400, blank=True, null=True)
    youtube = models.URLField(max_length=400, blank=True, null=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.first_name} - {self.user.last_name}'


def post_save_receiver(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


post_save.connect(post_save_receiver, sender=CustomUser)