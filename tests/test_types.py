from json import loads as json_loads
from rafter import Rafter
from sanic.response import json
from rafter_openapi import openapi_blueprint, doc


def test_list_default():
    app = Rafter(name='test_get')

    app.blueprint(openapi_blueprint)

    @app.get('/test')
    @doc.consumes(doc.List(int, description="All the numbers"),
                  location="body")
    def test(request):
        return json({"test": True})

    request, response = app.test_client.get('/openapi/spec.json')

    response_schema = json_loads(response.body.decode())
    parameter = response_schema['paths']['/test']['get']['parameters'][0]

    assert response.status == 200
    assert parameter['type'] == 'array'
    assert parameter['items']['type'] == 'integer'
