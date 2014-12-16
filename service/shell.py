from importlib import import_module

from . import control
from .utils import start_python_console
from .transports import (
    https,
    local,
)


class Shell(object):

    version = '0.0.1'
    dev_endpoint = 'http://127.0.0.1:8000'

    relevant_classes = (
        control.Client,
        local.LocalTransport,
        https.HttpsTransport,
    )

    def __init__(self):
        self.vars = {}

    def start(self):
        print('\nrhlabs soa shell version: %s' % (self.version,))
        self.populate_vars()
        self.print_help()
        start_python_console(self.vars)

    def populate_vars(self, action_response=None, response=None):
        self.vars['Client'] = control.Client
        self.vars['HttpsTransport'] = https.HttpsTransport
        self.vars['local_transport'] = local.instance
        self.vars['shelp'] = self.print_help
        self.vars['use_default_registry'] = self.use_default_registry
        self.vars['use_dev_endpoints'] = self.use_dev_endpoints
        self.vars['get_client_for_service'] = self.get_client_for_service
        self.vars['action_response'] = action_response
        self.vars['response'] = response

    def use_default_registry(self):
        request_registry = import_module('protobufs.request_registry_pb2')
        response_registry = import_module('protobufs.response_registry_pb2')

        control.set_protobufs_request_registry(request_registry)
        control.set_protobufs_response_registry(response_registry)

    def get_client_for_service(self, service_name):
        client = control.Client(
            service_name,
            post_call_action_hook=self.populate_vars,
        )
        self.use_default_registry()
        self.use_dev_endpoints(client)
        self.vars['client'] = client
        return client

    def use_dev_endpoints(self, client):
        client.set_transport(https.HttpsTransport())
        client.transport.set_endpoint(client.service_name, self.dev_endpoint)

    def print_help(self):
        print('\n')
        self.p('Available SOA objects:')
        for k, v in sorted(self.vars.items()):
            if self._is_relevant(v):
                self.p("  %-10s %s" % (k, v))
        print('\n')
        self.p('Useful shortcuts:')
        self.p('  shelp()                                   Shell help (print this help)')
        self.p('  get_client_for_service(<service_name>)    Return a dev client for the given service')
        self.p('  use_default_registry()                    Use the default registry (requires "protobufs" be installed)')

    def p(self, line=''):
        print("[soa] %s" % line)

    def _is_relevant(self, value):
        try:
            return (
                isinstance(value, self.relevant_classes) or
                issubclass(value, self.relevant_classes)
            )
        except TypeError:
            return False
