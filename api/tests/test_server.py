# Test cases can be run with:
# nosetests
# coverage report -m

import unittest
import json
import server

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPetServer(unittest.TestCase):

    def setUp(self):
        server.app.debug = True
        server.Pet.remove_all()
        server.Pet(0, 'fido', 'dog').save()
        server.Pet(0, 'kitty', 'cat').save()
        self.app = server.app.test_client()

    def test_index(self):
        resp = self.app.get('/')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        self.assertTrue ('Pet Demo REST API Service' in resp.data)

    def test_get_pet_list(self):
        resp = self.app.get('/pets')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertEqual( len(data), 2 )

    def test_get_pet(self):
        resp = self.app.get('/pets/2')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertEqual (data['name'], 'kitty')

    def test_get_pet_not_found(self):
        resp = self.app.get('/pets/0')
        self.assertEqual( resp.status_code, HTTP_404_NOT_FOUND )

    def test_create_pet(self):
        # save the current number of pets for later comparrison
        pet_count = self.get_pet_count()
        # add a new pet
        new_pet = {'name': 'sammy', 'category': 'snake'}
        data = json.dumps(new_pet)
        resp = self.app.post('/pets', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_201_CREATED )
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue( location != None)
        # Check the data is correct
        print ">>> Respose: {}".format(resp.data)
        new_json = json.loads(resp.data)
        self.assertEqual (new_json['name'], 'sammy')
        # check that count has gone up and includes sammy
        resp = self.app.get('/pets')
        # print 'resp_data(2): ' + resp.data
        data = json.loads(resp.data)
        self.assertEqual( resp.status_code, HTTP_200_OK )
        self.assertEqual( len(data), pet_count + 1 )
        self.assertIn( new_json, data )

    def test_update_pet(self):
        new_kitty = {'name': 'kitty', 'category': 'tabby'}
        data = json.dumps(new_kitty)
        resp = self.app.put('/pets/2', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        resp = self.app.get('/pets/2', content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        new_json = json.loads(resp.data)
        self.assertEqual (new_json['category'], 'tabby')

    def test_update_pet_with_no_name(self):
        new_pet = {'category': 'dog'}
        data = json.dumps(new_pet)
        resp = self.app.put('/pets/2', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_400_BAD_REQUEST )

    def test_update_pet_not_found(self):
        new_kitty = {"name": "timothy", "category": "mouse"}
        data = json.dumps(new_kitty)
        resp = self.app.put('/pets/0', data=data, content_type='application/json')
        self.assertEquals( resp.status_code, HTTP_404_NOT_FOUND )

    def test_delete_pet(self):
        # save the current number of pets for later comparrison
        pet_count = self.get_pet_count()
        # delete a pet
        resp = self.app.delete('/pets/2', content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_204_NO_CONTENT )
        self.assertEqual( len(resp.data), 0 )
        new_count = self.get_pet_count()
        self.assertEqual( new_count, pet_count - 1)

    def test_create_pet_with_no_name(self):
        new_pet = {'category': 'dog'}
        data = json.dumps(new_pet)
        resp = self.app.post('/pets', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, HTTP_400_BAD_REQUEST )

    def test_create_pet_with_no_content_type(self):
        new_pet = {'category': 'dog'}
        data = json.dumps(new_pet)
        resp = self.app.post('/pets', data=data)
        self.assertEqual( resp.status_code, HTTP_400_BAD_REQUEST )

    def test_get_nonexisting_pet(self):
        resp = self.app.get('/pets/5')
        self.assertEqual( resp.status_code, HTTP_404_NOT_FOUND )

    def test_query_pet_list_by_category(self):
        resp = self.app.get('/pets', query_string='category=dog')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        self.assertTrue( len(resp.data) > 0 )
        self.assertTrue( 'fido' in resp.data)
        self.assertFalse( 'kitty' in resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['category'], 'dog')

    def test_query_pet_list_by_name(self):
        resp = self.app.get('/pets', query_string='name=fido')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        self.assertTrue( len(resp.data) > 0 )
        print resp.data
        self.assertTrue( 'fido' in resp.data)
        self.assertFalse( 'kitty' in resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['name'], 'fido')

    def test_method_not_allowed(self):
        resp = self.app.post('/pets/0')
        self.assertEqual( resp.status_code, HTTP_405_METHOD_NOT_ALLOWED )

######################################################################
# Utility functions
######################################################################

    def get_pet_count(self):
        # save the current number of pets
        resp = self.app.get('/pets')
        self.assertEqual( resp.status_code, HTTP_200_OK )
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
