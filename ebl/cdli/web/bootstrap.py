import falcon

from ebl.cdli.web.cdli import CdliResource


def create_cdli_routes(api: falcon.API, spec):
    cdli = CdliResource()

    api.add_route('/cdli/{cdli_number}', cdli)

    spec.path(resource=cdli)
