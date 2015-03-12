import service.control
from service import exceptions

from . import base


class SampleServer(service.control.Server):
    service_name = 'simple'
    actions = {
        'simple_action': base.SimpleAction,
        'another_action': base.AnotherAction,
        'paginated_action': base.PaginatedAction,
    }


class AuthExemptServer(SampleServer):
    auth_exempt_actions = ('simple_action',)


class TestClient(base.TestCase):

    def setUp(self):
        super(TestClient, self).setUp()
        service.control.localize_server(SampleServer)
        self.client = service.control.Client('simple', token='test-token')

    def tearDown(self):
        service.control.unlocalize_server(SampleServer)

    def test_client_call_action(self):
        response = self.client.call_action(
            'simple_action',
            echo='echo!',
            lurker='still here',
        )

        self.assertTrue(response.success)
        self.assertEqual(response.result.answer, 'echo!')
        self.assertEqual(response.result.lurker, 'still here')

    def test_client_call_action_unrecognized_service(self):
        client = service.control.Client('invalid')
        with self.assertRaises(exceptions.UnrecognizedService):
            client.call_action('simple_action')

    def test_client_call_action_unrecognized_action(self):
        with self.assertRaises(exceptions.UnrecognizedAction):
            self.client.call_action('invalid')

    def test_client_call_action_rogue_parameter(self):
        with self.assertRaises(exceptions.RogueParameter):
            self.client.call_action('simple_action', invalid=True)

    def test_client_call_action_nested_params(self):
        response = self.client.call_action(
            'another_action',
            test='test',
            nested={'echo': 'echo!'},
        )
        self.assertTrue(response.success)

    def test_client_call_action_pagination(self):
        response = self.client.call_action(
            'paginated_action',
            echo='echo',
            total=100,
            control={'paginator': {'page_size': 25}},
        )
        self.assertTrue(response.success)
        self.assertFalse(response.control.paginator.HasField('previous_page'))
        self.assertEqual(response.control.paginator.next_page, 2)

        response = self.client.call_action(
            'paginated_action',
            echo='echo',
            total=100,
            control={'paginator': {'page': response.control.paginator.next_page, 'page_size': 25}},
        )
        self.assertTrue(response.success)
        # given a default page size of 25, the first echo should be suffixed
        # with "25" (0-24 being in the first page)
        self.assertTrue(response.result.echos[0].endswith('25'))
        self.assertEqual(response.control.paginator.count, 100)
        self.assertEqual(response.control.paginator.total_pages, 4)

        response = self.client.call_action(
            'paginated_action',
            echo='echo',
            total=100,
            control={'paginator': {'page': 4, 'page_size': 25}},
        )
        self.assertTrue(response.success)
        self.assertTrue(response.result.echos[0].endswith('75'))

    def test_client_call_action_specify_page_size(self):
        response = self.client.call_action(
            'paginated_action',
            echo='echo',
            total=100,
            control={'paginator': {'page_size': 3}},
        )
        self.assertTrue(response.success)
        self.assertEqual(response.control.paginator.count, 100)
        self.assertEqual(response.control.paginator.page_size, 3)
        # total pages should equal total / page_size
        self.assertEqual(response.control.paginator.total_pages, 34)
        self.assertTrue(response.result.echos[0].endswith('0'))

    def test_client_call_action_last_page(self):
        response = self.client.call_action(
            'paginated_action',
            echo='echo',
            total=10,
            control={'paginator': {'page_size': 5, 'page': 2}},
        )
        self.assertEqual(response.control.paginator.count, 10)
        self.assertFalse(response.control.paginator.HasField('next_page'))

    def test_client_call_action_last_page_request_specifies_next_page(self):
        response = self.client.call_action(
            'paginated_action',
            echo='echo',
            total=10,
            control={'paginator': {'page_size': 5, 'page': 2, 'next_page': 2}},
        )
        self.assertEqual(response.control.paginator.count, 10)
        self.assertFalse(response.control.paginator.HasField('next_page'))

    def test_client_call_action_last_page_request_specifies_previous_page(self):
        response = self.client.call_action(
            'paginated_action',
            echo='echo',
            total=10,
            control={'paginator': {'page_size': 5, 'previous_page': 1}},
        )
        self.assertEqual(response.control.paginator.count, 10)
        self.assertFalse(response.control.paginator.HasField('previous_page'))

    def test_client_call_action_over_max_page(self):
        with self.assertRaises(self.client.CallActionError) as expected:
            self.client.call_action(
                'paginated_action',
                echo='echo',
                total=100,
                control={'paginator': {'page_size': 1000}},
            )

        response = expected.exception.response
        self.assertFalse(response.success)
        self.assertIn('FIELD_ERROR', response.errors)
        field_error = response.error_details[0]
        self.assertEqual('paginator.page_size', field_error.key)
        self.assertEqual(field_error.detail, 'OVER_MAXIMUM')

    def test_client_call_action_on_error(self):
        with self.assertRaises(ValueError):
            self.client.call_action(
                'paginated_action',
                echo='echo',
                control={'paginator': {'page_size': 1000}},
                on_error=ValueError('exception'),
            )


class TestAuthExemptActions(base.TestCase):

    def setUp(self):
        super(TestAuthExemptActions, self).setUp()
        service.control.localize_server(AuthExemptServer)
        self.client = service.control.Client('simple')

    def tearDown(self):
        service.control.unlocalize_server(AuthExemptServer)

    def test_client_call_auth_exempt_action(self):
        response = self.client.call_action(
            'simple_action',
            echo='echo!',
        )

        self.assertTrue(response.success)
        self.assertEqual(response.result.answer, 'echo!')

    def test_client_non_auth_exempt_action(self):
        with self.assertRaises(self.client.CallActionError) as expected:
            self.client.call_action(
                'another_action',
                test='test',
            )

        response = expected.exception.response
        self.assertFalse(response.success)
        self.assertIn('FORBIDDEN', response.errors)
