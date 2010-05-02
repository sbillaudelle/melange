import gobject
import gtk
import cairo

import webkit
import javascriptcore as jscore

from httpserver import HOST, PORT

class Container(gobject.GObject):

    __gtype_name__ = 'Container'
    __gsignals__ = {
        }

    def __init__(self):

        gobject.GObject.__init__(self)

        self.window = gtk.Window()
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)
        self.window.stick()
        self.window.set_keep_below(True)
        self.window.set_decorated(False)
        self.window.set_app_paintable(True)
        self.window.set_skip_pager_hint(True)
        self.window.set_skip_taskbar_hint(True)
        self.window.connect('expose-event', self.expose_cb)

        self.window.move(100, 100)

        self.window.set_property('accept-focus', False)

        self.screen = self.window.get_screen()
        self.window.resize(self.screen.get_width(), self.screen.get_height())
        self.window.set_colormap(self.screen.get_rgba_colormap())

        self.view = webkit.WebView()
        self.view.set_transparent(True)
        self.view.connect('load-finished', self.load_finished_cb)
        self.view.open('http://{0}:{1}/container/container.html'.format(HOST, PORT))

        self.js_context = jscore.JSContext(self.view.get_main_frame().get_global_context()).globalObject

        self.window.add(self.view)

        self.window.set_opacity(0)
        self.window.show_all()

        self.widgets = {}


    def add_widget(self, widget):

        self.widgets[widget.instance] = widget
        widget.connect('resize', self.widget_resize_cb)
        widget.window.set_transient_for(self.window)

        self.calculate_size()


    def widget_resize_cb(self, widget, width, height):
        self.calculate_size()


    def load_finished_cb(self, view, frame):
        self.calculate_size()
        self.window.set_opacity(1)


    def calculate_size(self):

        container_x, container_y = self.window.get_position()

        width = 0
        height = 0
        for w in self.widgets.itervalues():
            w.set_position(container_x + width + 10, container_y + 10)
            width += w.get_size()[0]
            height = max(height, w.get_size()[1])

        self.resize(width, height)


    def resize(self, width, height):

        self.window.set_size_request(width + 20, height + 20)
        self.window.resize(width + 20, height + 20)
        try:
            self.js_context.resize(width, height)
        except AttributeError:
            pass


    def set_position(self, x, y):
        self.window.move(x, y)


    def show(self):
        self.window.show_all()


    def expose_cb(self, source, event):
        """ Clear the container's background. """

        ctx = source.window.cairo_create()

        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.paint()
