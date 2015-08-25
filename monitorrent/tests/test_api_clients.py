import json
import falcon
from mock import MagicMock
from ddt import ddt, data
from monitorrent.tests import RestTestBase
from monitorrent.rest.clients import ClientCollection, Client, ClientCheck
from monitorrent.plugin_managers import ClientsManager


@ddt
class ClientCollectionTest(RestTestBase):
    class TestClient(object):
        form = {}

    def test_get_all(self):
        clients_manager = ClientsManager({'test': ClientCollectionTest.TestClient()})

        client_collection = ClientCollection(clients_manager)
        self.api.add_route('/api/clients', client_collection)

        body = self.simulate_request('/api/clients')

        self.assertEqual(self.srmock.status, falcon.HTTP_OK)
        self.assertTrue('application/json' in self.srmock.headers_dict['Content-Type'])

        result = json.loads(body[0])

        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))

        self.assertEqual(result[0], {'name': 'test', 'form': ClientCollectionTest.TestClient.form})


class ClientTest(RestTestBase):
    def test_get_settings(self):
        clients_manager = ClientsManager({'test': ClientCollectionTest.TestClient()})
        settings = {'login': 'login'}
        clients_manager.get_settings = MagicMock(return_value=settings)

        client = Client(clients_manager)
        self.api.add_route('/api/clients/{client}', client)

        body = self.simulate_request('/api/clients/{0}'.format(1))
        self.assertEqual(self.srmock.status, falcon.HTTP_OK)
        self.assertTrue('application/json' in self.srmock.headers_dict['Content-Type'])

        result = json.loads(body[0])

        self.assertIsInstance(result, dict)
        self.assertEqual(result, settings)

    def test_empty_get_settings(self):
        clients_manager = ClientsManager({'test': ClientCollectionTest.TestClient()})
        clients_manager.get_settings = MagicMock(return_value=None)

        client = Client(clients_manager)
        client.__no_auth__ = True
        self.api.add_route('/api/clients/{client}', client)

        body = self.simulate_request('/api/clients/{0}'.format(1))
        self.assertEqual(self.srmock.status, falcon.HTTP_OK)
        self.assertTrue('application/json' in self.srmock.headers_dict['Content-Type'])

        result = json.loads(body[0])

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    def test_not_found_settings(self):
        clients_manager = ClientsManager({'test': ClientCollectionTest.TestClient()})
        clients_manager.get_settings = MagicMock(side_effect=KeyError)

        client = Client(clients_manager)
        self.api.add_route('/api/clients/{client}', client)

        self.simulate_request('/api/clients/{0}'.format(1))

        self.assertEqual(self.srmock.status, falcon.HTTP_NOT_FOUND)
        self.assertTrue('application/json' in self.srmock.headers_dict['Content-Type'])

    def test_successful_update_settings(self):
        clients_manager = ClientsManager({'test': ClientCollectionTest.TestClient()})
        clients_manager.set_settings = MagicMock(return_value=True)

        client = Client(clients_manager)
        self.api.add_route('/api/clients/{client}', client)

        self.simulate_request('/api/clients/{0}'.format(1), method="PUT",
                              body=json.dumps({'login': 'login', 'password': 'password'}))
        self.assertEqual(self.srmock.status, falcon.HTTP_NO_CONTENT)

    def test_not_found_update_settings(self):
        clients_manager = ClientsManager({'test': ClientCollectionTest.TestClient()})
        clients_manager.set_settings = MagicMock(side_effect=KeyError)

        client = Client(clients_manager)
        self.api.add_route('/api/clients/{client}', client)

        self.simulate_request('/api/clients/{0}'.format(1), method="PUT",
                              body=json.dumps({'login': 'login', 'password': 'password'}))
        self.assertEqual(self.srmock.status, falcon.HTTP_NOT_FOUND)

    def test_failed_update_settings(self):
        clients_manager = ClientsManager({'test': ClientCollectionTest.TestClient()})
        clients_manager.set_settings = MagicMock(return_value=False)

        client = Client(clients_manager)
        self.api.add_route('/api/clients/{client}', client)

        self.simulate_request('/api/clients/{0}'.format(1), method="PUT",
                              body=json.dumps({'login': 'login', 'password': 'password'}))
        self.assertEqual(self.srmock.status, falcon.HTTP_BAD_REQUEST)


@ddt
class CheckClientTest(RestTestBase):
    @data(True, False)
    def test_check_client(self, value):
        clients_manager = ClientsManager({'test': ClientCollectionTest.TestClient()})
        clients_manager.check_connection = MagicMock(return_value=value)

        client = ClientCheck(clients_manager)
        client.__no_auth__ = True
        self.api.add_route('/api/clients/{client}/check', client)

        body = self.simulate_request('/api/clients/{0}/check'.format('tracker.org'))
        self.assertEqual(self.srmock.status, falcon.HTTP_OK)
        self.assertTrue('application/json' in self.srmock.headers_dict['Content-Type'])

        result = json.loads(body[0])

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {'status': value})

    def test_check_client_not_found(self):
        clients_manager = ClientsManager({'test': ClientCollectionTest.TestClient()})
        clients_manager.check_connection = MagicMock(side_effect=KeyError)

        client = ClientCheck(clients_manager)
        client.__no_auth__ = True
        self.api.add_route('/api/clients/{client}/check', client)

        self.simulate_request('/api/clients/{0}/check'.format('tracker.org'))
        self.assertEqual(self.srmock.status, falcon.HTTP_NOT_FOUND)
