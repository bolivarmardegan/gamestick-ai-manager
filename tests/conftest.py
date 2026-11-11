import pytest
from gamestick_ai.demo import create_demo
from gamestick_ai.config import validate_root


@pytest.fixture
def example(tmp_path):
    card=tmp_path/'card';pkg=tmp_path/'package';backups=tmp_path/'backups'
    create_demo(card,pkg)
    return validate_root(card),pkg,backups
