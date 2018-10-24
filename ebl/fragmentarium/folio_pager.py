import falcon
from ebl.require_scope import require_scope


class FolioPagerResource:
    # pylint: disable=R0903
    def __init__(self, fragmentarium):
        self._fragmentarium = fragmentarium

    @falcon.before(require_scope, 'read:fragments')
    def on_get(self, req, resp, folio_name, folio_number, number):
        # pylint: disable=R0913
        if not req.context['user'].can_read_folio(folio_name):
            raise falcon.HTTPForbidden()

        try:
            resp.media = (self
                          ._fragmentarium
                          .folio_pager(folio_name, folio_number, number))
        except KeyError:
            resp.status = falcon.HTTP_NOT_FOUND
