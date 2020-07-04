from django.test import TestCase
from .models import User
# Create your tests here.


class AuthTestCase(TestCase):
    def setUp(self):
        self = User.objects.create_user(
            phone='8653532106', password='roman1234')
        self.is_staff = True
        self.is_superuser = True
        self.is_active = True
        self.save()

    def testLogin(self):
        self.client.login(username='8653532106', password='roman1234')
