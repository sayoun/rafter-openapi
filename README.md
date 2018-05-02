# Rafter OpenAPI

Add UI and OpenAPI documentation to your Rafter API.


## Installation

```shell
pip install rafter-openapi
```

Add OpenAPI and Swagger UI:

```python
from rafter_openapi import swagger_blueprint, openapi_blueprint

app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
```

You'll now have a Swagger UI at the URL `/swagger`.
Your routes will be automatically categorized by their blueprints.

## Example

For an example Swagger UI, see the [Pet Store](http://petstore.swagger.io/)

## Usage

### Use simple decorators to document routes:

```python
from rafter_openapi import doc

@app.get("/user/<user_id:int>")
@doc.summary("Fetches a user by ID")
@doc.produces({ "user": { "name": str, "id": int } })
async def get_user(request, user_id):
    ...

@app.post("/user")
@doc.summary("Creates a user")
@doc.consumes(doc.JsonBody({"user": { "name": str }}), location="body")
async def create_user(request):
    ...
```

### Model your input/output

```python
class Car:
    make = str
    model = str
    year = int

class Garage:
    spaces = int
    cars = [Car]

@app.get("/garage")
@doc.summary("Gets the whole garage")
@doc.produces(Garage)
async def get_garage(request):
    return json({
        "spaces": 2,
        "cars": [{"make": "Nissan", "model": "370Z"}]
    })

```

### Get more descriptive

```python
class Car:
    make = doc.String("Who made the car")
    model = doc.String("Type of car.  This will vary by make")
    year = doc.Integer("4-digit year of the car", required=False)

class Garage:
    spaces = doc.Integer("How many cars can fit in the garage")
    cars = doc.List(Car, description="All cars in the garage")
```

### Specify a JSON body without extensive modeling

```python
garage = doc.JsonBody({
    "spaces": doc.Integer,
    "cars": [
        {
            "make": doc.String,
            "model": doc.String,
            "year": doc.Integer
        }
    ]
})

@app.post("/store/garage")
@doc.summary("Stores a garage object")
@doc.consumes(garage, content_type="application/json", location="body")
async def store_garage(request):
    store_garage(request.json)
    return json(request.json)
```

### Easily use a Schematics model through conversion

```python
from schematics import Model, types
from rafter.contrib.schematics import model_node

class CarSchema(Model):
    @model_node()
    class body(Model):
        make = types.StringType(required=True)
        model = types.StringType(required=True)
        year = types.IntType(required=True)

@app.post("/store/car")
@doc.summary("Stores a car object")
@doc.consumes(doc.from_model(CarSchema), content_type="application/json", location="body")
async def store_car(request):
    store_car(request.json)
    return json(request.json)
```

### Configure all the things

```python
app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'Car API'
app.config.API_DESCRIPTION = 'Car API'
app.config.API_TERMS_OF_SERVICE = 'Use with caution!'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']
app.config.API_CONTACT_EMAIL = 'sayoun@pm.me'
```

#### Including OpenAPI's host, basePath and security parameters

Just follow the OpenAPI 2.0 specification on this

```python
app.config.API_HOST = 'subdomain.host.ext'
app.config.API_BASEPATH = '/v2/api/'

app.config.API_SECURITY = [
    {
        'authToken': []
    }
]

app.config.API_SECURITY_DEFINITIONS = {
    'authToken': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Paste your auth token and do not forget to add "Bearer " in front of it'
    },
    'OAuth2': {
        'type': 'oauth2',
        'flow': 'application',
        'tokenUrl': 'https://your.authserver.ext/v1/token',
        'scopes': {
            'some_scope': 'Grants access to this API'
        }
    }
}
```

### Set responses for different HTTP status codes

```python
@app.get("/garage/<id>")
@doc.summary("Gets the whole garage")
@doc.produces(Garage)
@doc.response(404, {"message": str}, description="When the garage cannot be found")
async def get_garage(request, id):
    garage = some_fetch_function(id)
    return json(garage)
```
