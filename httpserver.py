import os
import json
import thread
from bottle import route, send_file, abort, run, request, debug

import cream.ipc
from cream.util import cached_property

_OBJECT_CACHE = {}
_MELANGE = None

class HttpServer(object):
    """
    HttpServer for serving static (HTML|JS|CSS) files and proxying DBus for
    javascript.

    Instantiated by the `melange.Melange` class.

    TODO: It's all an ugly hack. We need routing functions with `self`
    references, proper route-resolving, a non-global Melange reference, ...
    """
    def __init__(self, melange):

        global _MELANGE
        _MELANGE = melange


    @route(r'/widgets/:instance_hash/:skin/(?P<file>.*)')
    def widget_files(instance_hash, skin, file):

        w = _MELANGE.widget_instances[instance_hash]
        path = os.path.join(w.meta['path'], 'skins', w.skins[skin]['path'])
        return send_file(file, path)


    @route(r'/common/(?P<file>.*)')
    def common_files(file):

        path = os.path.join(_MELANGE._base_path, 'data')
        print send_file(file, path)
        return send_file(file, path)


    @route('/ipc/call', method='POST')
    def ipc_call():

        # TODO: cleanup!
        print request.POST
        bus, object, method, arguments, interface = (request.POST[k] for k in
            ('bus', 'object', 'method', 'arguments','interface'))

        cache_name = ':'.join((bus, object))
        obj = _OBJECT_CACHE.get(cache_name, None)
        if obj is None:
            obj = cream.ipc.get_object(bus, object, interface)
            _OBJECT_CACHE[cache_name] = obj

        method = getattr(obj, method)
        result = method(*json.loads(arguments))

        return json.dumps(result)


    def run(self):
        thread.start_new_thread(run, (), dict(host='127.0.0.1', port=8080, quiet=True))