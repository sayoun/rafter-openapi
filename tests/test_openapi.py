from rafter import Rafter
from rafter_openapi import openapi_blueprint


def test_get_docs():
    app = Rafter(name='test_get')
    app.blueprint(openapi_blueprint)

    request, response = app.test_client.get('/openapi/spec.json')
    assert response.status == 200
