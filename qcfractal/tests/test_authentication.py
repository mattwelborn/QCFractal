"""
Tests the on-node procedures compute capabilities.
"""

import qcfractal
from qcfractal import testing

import requests
import pytest

import qcfractal.interface as portal

_users = {
    "read": {
        "pw": "hello",
        "perm": ["read"]
    },
    "write": {
        "pw": "something",
        "perm": ["read", "write"]
    },
    "admin": {
        "pw": "something",
        "perm": ["read", "write", "compute", "admin"]
    }
}


@pytest.fixture(scope="module")
def sec_server(request):
    """
    Builds a server instance with the event loop running in a thread.
    """

    db_name = "qcf_local_server_auth_test"

    with testing.pristine_loop() as loop:

        # Build server, manually handle IOLoop (no start/stop needed)
        server = qcfractal.FractalServer(
            port=testing.find_open_port(), db_project_name=db_name, io_loop=loop, security="local")

        # Clean and re-init the databse
        server.db.client.drop_database(server.db._project_name)
        server.db.init_database()

        # Add local users
        for k, v in _users.items():
            r = server.db.add_user(k, _users[k]["pw"], _users[k]["perm"])

        with testing.active_loop(loop) as act:
            yield server


### Tests the compute queue stack
def test_security_auth_decline_none(sec_server):
    client = portal.FractalClient(sec_server.get_address())

    with pytest.raises(requests.exceptions.HTTPError):
        r = client.get_molecules([])

    with pytest.raises(requests.exceptions.HTTPError):
        r = client.add_molecules({})


def test_security_auth_decline_bad_user(sec_server):
    client = portal.FractalClient(sec_server.get_address(), username="hello", password="something")

    with pytest.raises(requests.exceptions.HTTPError):
        r = client.get_molecules([])

    with pytest.raises(requests.exceptions.HTTPError):
        r = client.add_molecules({})


def test_security_auth_accept(sec_server):

    client = portal.FractalClient(sec_server.get_address(), username="write", password=_users["write"]["pw"])

    r = client.add_molecules({})
    r = client.get_molecules([])