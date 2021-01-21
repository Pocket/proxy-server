from json.decoder import JSONDecodeError

import uvicorn
from starlette.responses import JSONResponse
from fastapi import FastAPI, Request
from app.adzerk.api import Api as AdZerk
from app.client import Client
from app.exceptions.base_exception import BaseException
from app.exceptions.missing_param import MissingParam
from app.exceptions.invalid_content_type import InvalidContentType
from app.exceptions.invalid_param import InvalidParam
from app.validation import is_valid_pocket_id
from app.provider.geo_provider import GeolocationProvider
from typing import Dict
from app.middleware.proxy_headers import ProxyHeadersMiddleware

app = FastAPI()

#Trust the X-Forwarded-For using
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

provider = GeolocationProvider()


@app.post('/spocs')
async def get_spocs(request: Request):
    required_params = set(['version', 'consumer_key', 'pocket_id'])
    optional_params = set(['site', 'placements', 'country', 'region'])
    req_params = await __get_request_params(request)
    return await call(request.client.host, req_params, required_params, optional_params=optional_params)


@app.delete('/user')
async def delete_user(json_data: Dict):
    pocket_id = json_data['pocket_id']
    adzerk_api = AdZerk(pocket_id=pocket_id)
    response = adzerk_api.delete_user()

    return {'status': int(response.status_code == 200)}, response.status_code


@app.get('/pulse')
async def pulse():
    return {'pulse': 'ok'}


@app.exception_handler(MissingParam)
@app.exception_handler(InvalidParam)
@app.exception_handler(InvalidContentType)
def handle_invalid_usage(request: Request, error: BaseException):
    response = error.to_dict()
    response['status_code'] = error.status_code
    return JSONResponse(status_code=error.status_code, content=response)


async def call(client_ip, req_params, required_params, optional_params=None):
    # first validate required parameters
    params = {k: v for k, v in req_params.items() if k in required_params}
    __validate_required_params(required_params, params)

    # then identify unknown parameters
    all_params = set([k for k in req_params.keys()])
    unknown_params = all_params - (optional_params | required_params)  # given params minus union of allowed
    if len(unknown_params) > 0:
        raise InvalidParam('Unrecognized parameters: {0}'.format(unknown_params))

    # finally add optional parameters to required parameters
    other_params = {k: v for k, v in req_params.items() if k in optional_params}

    # do some additional checking for placements
    if 'placements' in other_params:
        __validate_placements(other_params['placements'])
    params.update(other_params)

    client = Client(ip=client_ip, geolocation_provider=provider, **params)

    return client.get_spocs()


def __validate_required_params(required, params):
    missing = required - params.keys()
    if missing:
        raise MissingParam('Missing required argument(s): {0}'.format(', '.join(missing)))

    if not is_valid_pocket_id(params['pocket_id']):
        raise InvalidParam('Invalid pocket_id')


def __validate_placements(placements):
    if not placements or len(placements) == 0:
        return
    required_params = ['name']
    optional_params = ['zone_ids', 'ad_types', 'count']
    list_params = ['ad_types', 'zone_ids']
    for p in placements:
        __validate_single_placement(p, required_params, optional_params, list_params)


def __validate_single_placement(placement, required, optional, list_params):
    for r in required:
        if r not in placement:
            raise MissingParam('Missing required parameter {0} in placement field'.format(r))
    for f in placement.keys():
        if f not in required and f not in optional:
            raise InvalidParam('{0} is an unknown placement parameter'.format(f))
    for l in list_params:
        if l in placement and type(placement[l]) is not list:
            raise InvalidParam('{0} must be a list of values in placement field'.format(l))


async def __get_request_params(request: Request):
    """
    Copies request params into a mutable dictionary
    so that we can put in a default value for site if not present.
    Default value is None so that we can grab it from
    hardcoded conf.
    :return:
    """
    try:
        json = await request.json()
    except JSONDecodeError:
        raise InvalidContentType('Expecting application/json body')

    req_params = dict()

    for k, v in json.items():
        req_params.update({k: v})
    for k, v in request.query_params.items():
        if k in ('site', 'country', 'region'):
            req_params.update({k: v})
    if 'site' not in req_params:
        req_params.update({'site': None})
    if 'placements' not in req_params:
        req_params.update({'placements': None})

    return req_params


if __name__ == "__main__":
    # This runs uvicorn in a local development environment.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
