from ddt import ddt, data
from mock import Mock, MagicMock, patch
from monitorrent.tests import TestCase
from monitorrent.plugin_managers import ClientsManager


@ddt
class ClientsManagerTest(TestCase):
    CLIENT1_NAME = 'client1'
    CLIENT2_NAME = 'client2'

    def setUp(self):
        super(ClientsManagerTest, self).setUp()

        self.client1 = Mock()
        self.client2 = Mock()

        self.clients_manager = ClientsManager({self.CLIENT1_NAME: self.client1, self.CLIENT2_NAME: self.client2})

    def test_get_settings(self):
        settings1 = {'login': 'login1', 'password': 'password1'}
        settings2 = {'login': 'login2', 'password': 'password2'}

        get_settings1_mock = MagicMock(return_value=settings1)
        get_settings2_mock = MagicMock(return_value=settings2)
        self.client1.get_settings = get_settings1_mock
        self.client2.get_settings = get_settings2_mock

        settings = self.clients_manager.get_settings(self.CLIENT1_NAME)

        self.assertEqual(settings1, settings)

        get_settings1_mock.assert_called_with()
        get_settings2_mock.assert_not_called()

    def test_set_settings(self):
        settings = {'login': 'login2', 'password': 'password2'}

        set_settings1_mock = MagicMock(return_value=True)
        set_settings2_mock = MagicMock(return_value=True)
        self.client1.set_settings = set_settings1_mock
        self.client2.set_settings = set_settings2_mock

        self.assertTrue(self.clients_manager.set_settings(self.CLIENT1_NAME, settings))

        set_settings1_mock.assert_called_with(settings)
        set_settings2_mock.assert_not_called()

    @data(True, False)
    def test_check_connection(self, value):
        check_connection_mock1 = MagicMock(return_value=value)
        check_connection_mock2 = MagicMock(return_value=value)
        self.client1.check_connection = check_connection_mock1
        self.client2.check_connection = check_connection_mock2

        self.assertEqual(value, self.clients_manager.check_connection(self.CLIENT1_NAME))
        self.assertEqual(value, self.clients_manager.check_connection(self.CLIENT2_NAME))

        check_connection_mock1.assert_called_once_with()
        check_connection_mock2.assert_called_once_with()

    def test_find_torrent_true(self):
        result = {'name': 'movie.torrent'}
        find_torrent_mock1 = MagicMock(return_value=None)
        find_torrent_mock2 = MagicMock(return_value=result)
        self.client1.find_torrent = find_torrent_mock1
        self.client2.find_torrent = find_torrent_mock2

        torrent_hash = 'hash'
        self.assertEqual(result, self.clients_manager.find_torrent(torrent_hash))

        find_torrent_mock1.assert_called_once_with(torrent_hash)
        find_torrent_mock2.assert_called_once_with(torrent_hash)

    def test_find_torrent_false(self):
        find_torrent_mock1 = MagicMock(return_value=None)
        find_torrent_mock2 = MagicMock(return_value=None)
        self.client1.find_torrent = find_torrent_mock1
        self.client2.find_torrent = find_torrent_mock2

        torrent_hash = 'hash'
        self.assertFalse(self.clients_manager.find_torrent(torrent_hash))

        find_torrent_mock1.assert_called_once_with(torrent_hash)
        find_torrent_mock2.assert_called_once_with(torrent_hash)

    def test_add_torrent_true(self):
        add_torrent_mock1 = MagicMock(return_value=False)
        add_torrent_mock2 = MagicMock(return_value=True)
        self.client1.add_torrent = add_torrent_mock1
        self.client2.add_torrent = add_torrent_mock2

        torrent = '!torrent_file'
        self.assertTrue(self.clients_manager.add_torrent(torrent))

        add_torrent_mock1.assert_called_once_with(torrent)
        add_torrent_mock2.assert_called_once_with(torrent)

    def test_add_torrent_false(self):
        add_torrent_mock1 = MagicMock(return_value=False)
        add_torrent_mock2 = MagicMock(return_value=False)
        self.client1.add_torrent = add_torrent_mock1
        self.client2.add_torrent = add_torrent_mock2

        torrent = '!torrent_file'
        self.assertFalse(self.clients_manager.add_torrent(torrent))

        add_torrent_mock1.assert_called_once_with(torrent)
        add_torrent_mock2.assert_called_once_with(torrent)

    def test_remove_torrent_true(self):
        remove_torrent_mock1 = MagicMock(return_value=False)
        remove_torrent_mock2 = MagicMock(return_value=True)
        self.client1.remove_torrent = remove_torrent_mock1
        self.client2.remove_torrent = remove_torrent_mock2

        torrent_hash = 'hash'
        self.assertTrue(self.clients_manager.remove_torrent(torrent_hash))

        remove_torrent_mock1.assert_called_once_with(torrent_hash)
        remove_torrent_mock2.assert_called_once_with(torrent_hash)

    def test_remove_torrent_false(self):
        remove_torrent_mock1 = MagicMock(return_value=False)
        remove_torrent_mock2 = MagicMock(return_value=False)
        self.client1.remove_torrent = remove_torrent_mock1
        self.client2.remove_torrent = remove_torrent_mock2

        torrent_hash = 'hash'
        self.assertFalse(self.clients_manager.remove_torrent(torrent_hash))

        remove_torrent_mock1.assert_called_once_with(torrent_hash)
        remove_torrent_mock2.assert_called_once_with(torrent_hash)

    def test_get_plugins(self):
        clients = self.clients_manager.clients
        get_plugins_mock = Mock(return_value=clients)
        with patch('monitorrent.plugin_managers.get_plugins', get_plugins_mock):
            self.clients_manager = ClientsManager()

        self.assertEqual(clients, self.clients_manager.clients)
