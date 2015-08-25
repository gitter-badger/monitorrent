from mock import Mock, MagicMock, patch
from sqlalchemy import Column, Integer, ForeignKey
from monitorrent.db import DBSession, row2dict
from monitorrent.plugins.trackers import Topic
from monitorrent.tests import TestCase, DbTestCase
from monitorrent.plugins.trackers import TrackerPluginBase, TrackerPluginWithCredentialsBase
from monitorrent.plugin_managers import TrackersManager

TRACKER1_PLUGIN_NAME = 'tracker1.com'
TRACKER2_PLUGIN_NAME = 'tracker2.com'


class Tracker1Topic(Topic):
    __tablename__ = "tracker1_topics"

    id = Column(Integer, ForeignKey('topics.id'), primary_key=True)
    some_addition_field = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': TRACKER1_PLUGIN_NAME
    }


class Tracker1(TrackerPluginBase):
    def parse_url(self, url):
        pass

    def can_parse_url(self, url):
        pass

    def _prepare_request(self, topic):
        pass


class Tracker2(TrackerPluginWithCredentialsBase):
    def parse_url(self, url):
        pass

    def can_parse_url(self, url):
        pass

    def _prepare_request(self, topic):
        pass

    def login(self):
        pass

    def verify(self):
        pass


class TrackersManagerTest(TestCase):
    def test_get_settings(self):
        tracker1 = Tracker1()
        tracker2 = Tracker2()
        trackers_manager = TrackersManager({
            TRACKER1_PLUGIN_NAME: tracker1,
            TRACKER2_PLUGIN_NAME: tracker2,
        })

        self.assertIsNone(trackers_manager.get_settings(TRACKER1_PLUGIN_NAME))

        credentials2 = {'login': 'username'}
        get_credentials_mock = MagicMock(return_value=credentials2)
        tracker2.get_credentials = get_credentials_mock

        self.assertEqual(trackers_manager.get_settings(TRACKER2_PLUGIN_NAME), credentials2)

        get_credentials_mock.assert_called_with()

    def test_set_settings(self):
        tracker1 = Tracker1()
        tracker2 = Tracker2()
        trackers_manager = TrackersManager({
            TRACKER1_PLUGIN_NAME: tracker1,
            TRACKER2_PLUGIN_NAME: tracker2,
        })

        credentials1 = {'login': 'username'}
        self.assertFalse(trackers_manager.set_settings(TRACKER1_PLUGIN_NAME, credentials1))

        credentials2 = {'login': 'username', 'password': 'password'}
        update_credentials_mock2 = MagicMock()
        tracker2.update_credentials = update_credentials_mock2

        self.assertTrue(trackers_manager.set_settings(TRACKER2_PLUGIN_NAME, credentials2))

        update_credentials_mock2.assert_called_with(credentials2)

    def test_check_connection(self):
        tracker1 = Tracker1()
        tracker2 = Tracker2()
        trackers_manager = TrackersManager({
            TRACKER1_PLUGIN_NAME: tracker1,
            TRACKER2_PLUGIN_NAME: tracker2,
        })

        self.assertFalse(trackers_manager.check_connection(TRACKER1_PLUGIN_NAME))

        verify_mock = MagicMock(return_value=True)
        tracker2.verify = verify_mock

        self.assertTrue(trackers_manager.check_connection(TRACKER2_PLUGIN_NAME))

        verify_mock.assert_called_with()

    def test_prepare_add_topic_1(self):
        tracker1 = Tracker1()
        tracker2 = Tracker2()
        trackers_manager = TrackersManager({
            TRACKER1_PLUGIN_NAME: tracker1,
            TRACKER2_PLUGIN_NAME: tracker2,
        })

        parsed_url = {'display_name': "Some Name / Translated Name"}
        prepare_add_topic_mock1 = MagicMock(return_value=parsed_url)
        tracker1.prepare_add_topic = prepare_add_topic_mock1
        result = trackers_manager.prepare_add_topic('http://tracker.com/1/')
        self.assertIsNotNone(result)

        prepare_add_topic_mock1.assert_called_with('http://tracker.com/1/')

        self.assertEqual(result, {'form': TrackerPluginBase.topic_form, 'settings': parsed_url})

    def test_prepare_add_topic_2(self):
        tracker1 = Tracker1()
        tracker2 = Tracker2()
        trackers_manager = TrackersManager({
            TRACKER1_PLUGIN_NAME: tracker1,
            TRACKER2_PLUGIN_NAME: tracker2,
        })

        prepare_add_topic_mock1 = MagicMock(return_value=None)
        tracker1.prepare_add_topic = prepare_add_topic_mock1

        parsed_url = {'display_name': "Some Name / Translated Name"}
        prepare_add_topic_mock2 = MagicMock(return_value=parsed_url)
        tracker2.prepare_add_topic = prepare_add_topic_mock2

        result = trackers_manager.prepare_add_topic('http://tracker.com/1/')
        self.assertIsNotNone(result)

        prepare_add_topic_mock1.assert_called_with('http://tracker.com/1/')
        prepare_add_topic_mock2.assert_called_with('http://tracker.com/1/')

        self.assertEqual(result, {'form': TrackerPluginBase.topic_form, 'settings': parsed_url})

    def test_prepare_add_topic_3(self):
        tracker1 = Tracker1()
        tracker2 = Tracker2()
        trackers_manager = TrackersManager({
            TRACKER1_PLUGIN_NAME: tracker1,
            TRACKER2_PLUGIN_NAME: tracker2,
        })

        prepare_add_topic_mock1 = MagicMock(return_value=None)
        tracker1.prepare_add_topic = prepare_add_topic_mock1

        prepare_add_topic_mock2 = MagicMock(return_value=None)
        tracker2.prepare_add_topic = prepare_add_topic_mock2

        result = trackers_manager.prepare_add_topic('http://tracker.com/1/')
        self.assertIsNone(result)

        prepare_add_topic_mock1.assert_called_with('http://tracker.com/1/')
        prepare_add_topic_mock2.assert_called_with('http://tracker.com/1/')

    def test_add_topic_1(self):
        tracker1 = Tracker1()
        tracker2 = Tracker2()
        trackers_manager = TrackersManager({
            TRACKER1_PLUGIN_NAME: tracker1,
            TRACKER2_PLUGIN_NAME: tracker2,
        })

        can_parse_url_mock1 = MagicMock(return_value=True)
        add_topic_mock1 = MagicMock(return_value=True)
        tracker1.can_parse_url = can_parse_url_mock1
        tracker1.add_topic = add_topic_mock1

        params = {'display_name': "Some Name / Translated Name"}
        url = 'http://tracker.com/1/'
        self.assertTrue(trackers_manager.add_topic(url, params))

        can_parse_url_mock1.assert_called_with(url)
        add_topic_mock1.assert_called_with(url, params)

    def test_add_topic_2(self):
        tracker1 = Tracker1()
        tracker2 = Tracker2()
        trackers_manager = TrackersManager({
            TRACKER1_PLUGIN_NAME: tracker1,
            TRACKER2_PLUGIN_NAME: tracker2,
        })

        can_parse_url_mock1 = MagicMock(return_value=False)
        add_topic_mock1 = MagicMock(return_value=False)
        tracker1.can_parse_url = can_parse_url_mock1
        tracker1.add_topic = add_topic_mock1

        can_parse_url_mock2 = MagicMock(return_value=True)
        add_topic_mock2 = MagicMock(return_value=True)
        tracker2.can_parse_url = can_parse_url_mock2
        tracker2.add_topic = add_topic_mock2

        params = {'display_name': "Some Name / Translated Name"}
        url = 'http://tracker.com/1/'
        self.assertTrue(trackers_manager.add_topic(url, params))

        can_parse_url_mock1.assert_called_with(url)
        add_topic_mock1.assert_not_called()

        can_parse_url_mock2.assert_called_with(url)
        add_topic_mock2.assert_called_with(url, params)

    def test_add_topic_3(self):
        tracker1 = Tracker1()
        tracker2 = Tracker2()
        trackers_manager = TrackersManager({
            TRACKER1_PLUGIN_NAME: tracker1,
            TRACKER2_PLUGIN_NAME: tracker2,
        })

        can_parse_url_mock1 = MagicMock(return_value=False)
        add_topic_mock1 = MagicMock(return_value=False)
        tracker1.can_parse_url = can_parse_url_mock1
        tracker1.add_topic = add_topic_mock1

        can_parse_url_mock2 = MagicMock(return_value=False)
        add_topic_mock2 = MagicMock(return_value=False)
        tracker2.can_parse_url = can_parse_url_mock2
        tracker2.add_topic = add_topic_mock2

        params = {'display_name': "Some Name / Translated Name"}
        url = 'http://tracker.com/1/'
        self.assertFalse(trackers_manager.add_topic(url, params))

        can_parse_url_mock1.assert_called_with(url)
        add_topic_mock1.assert_not_called()

        can_parse_url_mock2.assert_called_with(url)
        add_topic_mock2.assert_not_called()


class TrackersManagerDbPartTest(DbTestCase):
    DISPLAY_NAME1 = "Some Name / Translated Name"

    def setUp(self):
        super(TrackersManagerDbPartTest, self).setUp()

        with DBSession() as db:
            topic = Tracker1Topic(display_name=self.DISPLAY_NAME1,
                                  url="http://tracker.com/1/",
                                  type=TRACKER1_PLUGIN_NAME,
                                  some_addition_field=1)
            db.add(topic)
            db.commit()
            self.tracker1_id1 = topic.id

        self.tracker1 = Tracker1()
        self.tracker2 = Tracker2()
        self.trackers_manager = TrackersManager({
            TRACKER1_PLUGIN_NAME: self.tracker1,
            TRACKER2_PLUGIN_NAME: self.tracker2,
        })

    def test_remove_topic_1(self):
        self.assertTrue(self.trackers_manager.remove_topic(self.tracker1_id1))
        with DBSession() as db:
            topic = db.query(Topic).filter(Topic.id == self.tracker1_id1).first()
            self.assertIsNone(topic)

    def test_remove_topic_2(self):
        with self.assertRaises(KeyError):
            self.trackers_manager.remove_topic(self.tracker1_id1 + 1)
        with DBSession() as db:
            topic = db.query(Topic).filter(Topic.id == self.tracker1_id1).first()
            self.assertIsNotNone(topic)

    def test_get_topic_1(self):
        topic_settings = {'display_name': self.DISPLAY_NAME1}
        get_topic_mock = MagicMock(return_value=topic_settings)
        self.tracker1.get_topic = get_topic_mock

        result = self.trackers_manager.get_topic(self.tracker1_id1)

        self.assertEqual({'form': self.tracker1.topic_form, 'settings': topic_settings}, result)

        get_topic_mock.assert_called_with(self.tracker1_id1)

    def test_get_topic_2(self):
        with self.assertRaises(KeyError):
            self.trackers_manager.get_topic(self.tracker1_id1 + 1)

    def test_get_topic_3(self):
        remove_type = TRACKER1_PLUGIN_NAME + ".uk"

        with DBSession() as db:
            topic = Topic(display_name=self.DISPLAY_NAME1 + " / Test",
                          url="http://tracker.com/2/",
                          type=remove_type)
            result = db.execute(topic.__table__.insert(), row2dict(topic, fields=['display_name', 'url', 'type']))
            tracker1_id2 = result.inserted_primary_key[0]

        with self.assertRaises(KeyError):
            self.trackers_manager.get_topic(tracker1_id2)
