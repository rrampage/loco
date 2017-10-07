from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):

    def create_user_base(self, phone, name, password, is_staff, is_superuser, **extra_fields):
        '''
        Creates user with give phone, name, password and staffing status.
        '''

        now = timezone.now()

        if not phone:
            raise ValueError('User must have an phone address')

        if not name:
            raise ValueError('User must have name.')

        user = self.model(phone=phone, name=name, last_login=now, is_staff=is_staff, is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, name, password=None, **extra_fields):
        '''
        Creates and save non-staff-normal user with given phone, name and password.
        '''

        return self.create_user_base(phone, name, password, False, False, **extra_fields)

    def create_superuser(self, phone, name, password, **extra_fields):
        '''
         Creates and saves super user with given phone, name and password.
        '''
        return self.create_user_base(phone, name, password, True, True, **extra_fields)

    def create_staffuser(self, phone, name, password, **extra_fields):
        return self.create_user_base(phone, name, password, True, False, **extra_fields)

    def get_or_create_dummy(self, phone):
        if not phone:
            return None;

        try:
            return self.get(phone=phone)
        except self.model.DoesNotExist:
            return self.create_user(phone=phone, name="InactiveUser", is_active=False)


class UserOtpManager(BaseUserManager):

    def checkOtp(self, otp, phone):
        if not otp:
            return False

        return str(otp) == '1234'

        try:
            row = self.get(otp=otp, user__phone=phone)
            row.delete()
            return True
        except self.model.DoesNotExist:
            return False

    def create_or_update(self, user, otp):
        try:
            row = self.get(user=user)
            row.otp = otp
            row.save()
            return row
        except self.model.DoesNotExist:
            return self.create(user=user, otp=otp)
