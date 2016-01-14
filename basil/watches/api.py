import json

import falcon

import storage


def create_api(middleware):
    app = falcon.API(middleware=middleware)
    watches = WatchesResource()
    app.add_route('/watches', watches)
    watch = WatchResource()
    app.add_route('/watches/{by_id}', watch)
    return app


class WatchesResource(object):
    @staticmethod
    def on_get(req, resp):
        name_starts = req.get_param('name:starts', default=None)
        result = storage.Monitoring.find(req.context['session'], name_starts)
        found = [row.as_dict() for row in result if row.is_clean()]
        resp.body = json.dumps(found)
        resp.status = falcon.HTTP_200


class WatchResource(object):
    @staticmethod
    def on_get(req, resp, by_id):
        result = storage.Monitoring.get(req.context['session'], by_id)
        if result:
            resp.body = json.dumps(result.as_dict())
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404

    @staticmethod
    def on_put(req, resp, by_id):
        raw_body = req.stream.read()
        if not raw_body:
            raise falcon.HTTPBadRequest('A valid JSON document is required.')
        try:
            body = json.loads(raw_body.decode('utf-8'))
        except UnicodeDecodeError:
            msg = 'Non-UTF8 characters found in the request body'
            raise falcon.HTTPBadRequest(msg)
        except ValueError as e:
            msg = 'Could not parse the body as Json: {0}. Ignoring.'.format(e)
            raise falcon.HTTPBadRequest(msg)

        name = body['name']
        storage.Monitoring.create(req.context['session'], by_id, name)
        resp.add_link('/watches/%s' % by_id, 'self', title=name)
        resp.status = falcon.HTTP_201

    @staticmethod
    def on_delete(req, resp, by_id):
        storage.Monitoring.delete(req.context['session'], by_id)
        resp.status = falcon.HTTP_204
