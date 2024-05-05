from chaserland_api_gateway.bootstrap.app import create_sub_app

from .v1.app import auth_v1_app

description = """
## API Versions

### V1

#### Docs

- [docs](/auth/v1/docs)
- [redoc](/auth/v1/redoc)
- [openapi.json](/auth/v1/openapi.json)

#### Routes

- [health](/auth/v1/health)
- [oauth2](/auth/v1/oauth2)

"""

app = create_sub_app(title="Chaserland Auth API", description=description)

app.mount("/v1", auth_v1_app, name=auth_v1_app.title)
