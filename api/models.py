# from django.db import models
# from django.db.models.signals import post_save
# from django.contrib.auth.models import AbstractUser
# import qrcode
# from io import BytesIO
# from django.core.files import File

# class User(AbstractUser):
#     username = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     def profile(self):
#         return Profile.objects.get(user=self)

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     full_name = models.CharField(max_length=1000)
#     bio = models.CharField(max_length=100)
#     image = models.ImageField(upload_to="user_images", default="default.jpg")
#     verified = models.BooleanField(default=False)
#     qr_code = models.ImageField(upload_to='qr_codes', blank=True)

#     def save(self, *args, **kwargs):
#         if not self.full_name:
#             self.full_name = self.user.username

#         # Generate QR code
#         qr = qrcode.QRCode(version=1, box_size=10, border=5)
#         qr.add_data(self.user.id)
#         qr.make(fit=True)
#         img = qr.make_image(fill='black', back_color='white')

#         buffer = BytesIO()
#         img.save(buffer, 'PNG')
#         self.qr_code.save(f'{self.user.id}_qr.png', File(buffer), save=False)

#         super(Profile, self).save(*args, **kwargs)

#     @property
#     def sent_messages(self):
#         # Messages sent by the user
#         return ChatMessage.objects.filter(sender=self.user)

#     @property
#     def received_messages(self):
#         # Messages received by the user
#         return ChatMessage.objects.filter(reciever=self.user)

#     def message_history_with(self, other_user):
#         # All messages between self.user and other_user
#         return ChatMessage.objects.filter(
#             models.Q(sender=self.user, reciever=other_user) |
#             models.Q(sender=other_user, reciever=self.user)
#         ).order_by('date')

#     def search_by_qr_code(qr_code):
#         try:
#             profile = Profile.objects.get(qr_code=qr_code)
#             return profile.user
#         except Profile.DoesNotExist:
#             return None

# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

# post_save.connect(create_user_profile, sender=User)
# post_save.connect(save_user_profile, sender=User)

# class Todo(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=1000)
#     completed = models.BooleanField(default=False)
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title[:30]

# class ChatMessage(models.Model):
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user")
#     sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sender")
#     reciever = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reciever")
#     message = models.CharField(max_length=10000000000, blank=True, null=True)
#     file = models.FileField(upload_to='chat_files/', blank=True, null=True)
#     is_read = models.BooleanField(default=False)
#     date = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['date']
#         verbose_name_plural = "Messages"

#     def __str__(self):
#         return f"{self.sender} - {self.reciever}"

#     @property
#     def sender_profile(self):
#         return Profile.objects.get(user=self.sender)

#     @property
#     def reciever_profile(self):
#         return Profile.objects.get(user=self.reciever)


from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
import qrcode
from io import BytesIO
from django.core.files import File

class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def profile(self):
        return Profile.objects.get(user=self)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=1000)
    bio = models.CharField(max_length=100)
    image = models.ImageField(upload_to="user_images", default="default.jpg")
    verified = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True)

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.user.username

        # Generate QR code only if it doesn't already exist
        if not self.qr_code:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(self.user.id)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            buffer = BytesIO()
            img.save(buffer, 'PNG')
            self.qr_code.save(f'{self.user.id}_qr.png', File(buffer), save=False)

        super(Profile, self).save(*args, **kwargs)

    @property
    def sent_messages(self):
        return ChatMessage.objects.filter(sender=self.user)

    @property
    def received_messages(self):
        return ChatMessage.objects.filter(reciever=self.user)

    def message_history_with(self, other_user):
        return ChatMessage.objects.filter(
            models.Q(sender=self.user, reciever=other_user) |
            models.Q(sender=other_user, reciever=self.user)
        ).order_by('date')

    @staticmethod
    def search_by_qr_code(qr_code):
        try:
            profile = Profile.objects.get(qr_code=qr_code)
            return profile.user
        except Profile.DoesNotExist:
            return None

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    completed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title[:30]

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sender")
    reciever = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reciever")
    message = models.CharField(max_length=10000000000, blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.sender} - {self.reciever}"

    @property
    def sender_profile(self):
        return Profile.objects.get(user=self.sender)

    @property
    def reciever_profile(self):
        return Profile.objects.get(user=self.reciever)
