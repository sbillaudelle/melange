#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os
import thread
from bottle import route, send_file, abort, run, request

from common import HOST, PORT

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


    @route(r'/thingy/(?P<file>.*)')
    def thingy_files(file):

        path = os.path.join(_MELANGE.context.working_directory, 'data/thingy')
        return send_file(file, path)


    @route(r'/chrome/(?P<file>.*)')
    def chrome_files(file):

        theme = _MELANGE.config.default_theme
        path = os.path.dirname(_MELANGE.themes.get_by_id(theme)._path)

        return send_file(file, os.path.join(path, 'chrome'))


    @route(r'/widget/tmp/(?P<file>.*)')
    def tmp_files(file):

        instance = request.GET.get('instance')

        path = _MELANGE.widgets[request.GET['instance']].get_tmp()

        return send_file(file, path)


    @route(r'/widget/(?P<file>.*)')
    def widget_files(file):

        instance = request.GET.get('instance')

        skin = _MELANGE.widgets[request.GET['instance']].config.widget_skin

        w = _MELANGE.widgets[instance]
        path = os.path.join(w.context.working_directory, 'skins', os.path.dirname(w.skins.get_by_id(skin)._path))
        return send_file(file, path)


    @route(r'/common/(?P<file>.*)')
    def common_files(file):

        instance = request.GET.get('instance')
        if instance:
            widget = _MELANGE.widgets[instance]
            theme = widget.config.widget_theme
            if theme == 'use.the.fucking.global.settings.and.suck.my.Dick':
                theme =  _MELANGE.config.default_theme
            path = os.path.dirname(_MELANGE.themes.get_by_id(theme)._path)
        else:
            theme = _MELANGE.config.default_theme
            path = os.path.dirname(_MELANGE.themes.get_by_id(theme)._path)

        return send_file(file, path)

    def run(self):
        thread.start_new_thread(run, (), dict(host=HOST, port=PORT, quiet=True))
