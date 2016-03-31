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
        # handle input with media type: application/x-www-form-urlencoded
        if 'name' in req.params:
            name = req.get_param('name')
        else:
            body = WatchResource.read_body(req)
            name = WatchResource.get_attr_from(body, 'name')

        session = req.context['session']
        existing = storage.Monitoring.get(session, by_id)
        if existing:
            if existing.name != name:
                existing.name = name
                session.add(existing)
            resp.status = falcon.HTTP_204
        else:
            storage.Monitoring.create(session, by_id, name)
            resp.status = falcon.HTTP_201
        resp.add_link('/watches/%s' % by_id, 'self', title=name)

    @staticmethod
    def get_attr_from(body, attr):
        if attr in body:
            value = body[attr]
        else:
            raise falcon.HTTPBadRequest('Bad Request Invalid JSON',
                                        'Missing %s attribute' % attr)
        return value

    @staticmethod
    def read_body(req):
        raw_body = req.stream.read()
        msg = 'A valid JSON document is required.'
        if not raw_body:
            raise falcon.HTTPBadRequest(msg, 'No body found')
        try:
            body = json.loads(raw_body.decode('utf-8'))
        except UnicodeDecodeError:
            raise falcon.HTTPBadRequest(msg, 'Non-UTF8 characters found'
                                             ' in the request body')
        except ValueError as e:
            raise falcon.HTTPBadRequest(msg, 'Could not parse the body as'
                                             ' Json: {0}. Ignoring.' % e)
        return body

    @staticmethod
    def on_delete(req, resp, by_id):
        storage.Monitoring.delete(req.context['session'], by_id)
        resp.status = falcon.HTTP_204
