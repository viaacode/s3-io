import pytest
import connexion
from s3_io.s3io_api import create_app
flask_app = create_app()
#flask_app.add_api('api/s3io-api.yaml', arguments={'title': 'Swarm s3'})



@pytest.fixture(scope='module')
def client():
    with flask_app.app.test_client() as c:
        yield c


def test_health(client):
    response = client.get('/v1.0/health')
    assert response.status_code == 200