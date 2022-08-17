import shutil
from pathlib import Path
from tempfile import mkdtemp

import pytest
from click.testing import CliRunner

import ape

# NOTE: Ensure that we don't use local paths for these
ape.config.DATA_FOLDER = Path(mkdtemp()).resolve()
ape.config.PROJECT_FOLDER = Path(mkdtemp()).resolve()


@pytest.fixture(autouse=True)
def setenviron(monkeypatch):
    """
    Sets the APE_TESTING environment variable during tests.

    With this variable set fault handling and IPython command history logging
    will be disabled in the ape console.
    """
    monkeypatch.setenv("APE_TESTING", "1")


@pytest.fixture(scope="session")
def config():
    yield ape.config


@pytest.fixture(scope="session")
def data_folder(config):
    yield config.DATA_FOLDER


@pytest.fixture(scope="session")
def plugin_manager():
    yield ape.networks.plugin_manager


@pytest.fixture(scope="session")
def accounts():
    yield ape.accounts


@pytest.fixture(scope="session")
def compilers():
    yield ape.compilers


@pytest.fixture(scope="session")
def networks():
    yield ape.networks


@pytest.fixture(scope="session")
def chain():
    yield ape.chain


@pytest.fixture(scope="session")
def project_folder(config):
    yield config.PROJECT_FOLDER


@pytest.fixture(scope="session")
def project(config):
    yield ape.Project(config.PROJECT_FOLDER)


@pytest.fixture(scope="session")
def project_manager():
    return ape.project


@pytest.fixture(scope="session")
def dependency_manager(project_manager):
    return project_manager.dependency_manager


@pytest.fixture(scope="session")
def keyparams():
    # NOTE: password is 'a'
    return {
        "address": "7e5f4552091a69125d5dfcb7b8c2659029395bdf",
        "crypto": {
            "cipher": "aes-128-ctr",
            "cipherparams": {"iv": "7bc492fb5dca4fe80fd47645b2aad0ff"},
            "ciphertext": "43beb65018a35c31494f642ec535315897634b021d7ec5bb8e0e2172387e2812",
            "kdf": "scrypt",
            "kdfparams": {
                "dklen": 32,
                "n": 262144,
                "r": 1,
                "p": 8,
                "salt": "4b127cb5ddbc0b3bd0cc0d2ef9a89bec",
            },
            "mac": "6a1d520975a031e11fc16cff610f5ae7476bcae4f2f598bc59ccffeae33b1caa",
        },
        "id": "ee424db9-da20-405d-bd75-e609d3e2b4ad",
        "version": 3,
    }


@pytest.fixture(scope="session")
def temp_accounts_path(config):
    path = Path(config.DATA_FOLDER) / "accounts"
    path.mkdir(exist_ok=True, parents=True)

    yield path

    if path.exists():
        shutil.rmtree(path)


@pytest.fixture
def runner(project):
    yield CliRunner()


@pytest.fixture(scope="session")
def networks_connected_to_tester():
    with ape.networks.parse_network_choice("::test"):
        yield ape.networks


@pytest.fixture
def networks_disconnected(networks):
    provider = networks.active_provider
    networks.active_provider = None
    yield networks
    networks.active_provider = provider


@pytest.fixture(scope="session")
def ethereum(networks):
    return networks.ethereum


@pytest.fixture(scope="session")
def eth_tester_provider(networks_connected_to_tester):
    yield networks_connected_to_tester.provider


@pytest.fixture
def isolation(chain):
    snapshot = chain.snapshot()
    yield

    if snapshot:
        chain.restore(snapshot)
