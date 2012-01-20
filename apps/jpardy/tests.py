from django.test import TestCase

class JpardyViewsTest(TestCase):
    fixtures = ['test_data.json']

    def test_valid_login(self):
        resp = self.client.get('/login/')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('form' in resp.context)

        resp = self.client.post('/login/',
                                {'username': 'user1',
                                 'password': 'password1'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/home/')

    def test_invalid_login(self):
        resp = self.client.get('/login/')
        self.assertEquals(resp.status_code, 200)
        self.assertTrue('form' in resp.context)

        resp = self.client.post('/login/',
                                {'username': 'user1',
                                 'password': 'badpassword'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(not resp.context['user'].is_authenticated())

    def test_home_page(self):
        resp = self.client.get('/home/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'],
                         'http://testserver/login/?next=/home/')

        self.client.login(username='user1', password='password1')
        resp = self.client.get('/home/')
        self.assertEquals(resp.status_code, 200)
