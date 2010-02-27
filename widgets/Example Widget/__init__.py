from cream.contrib.melange import api

# This will register the API-class as `widget.example`
# accessable from your JavaScript code.
@api.register('example')
class Example(api.API):

    def __init__(self, widget):

        self.widget = widget


    def doit(self, arg):

        print "Got '{0}'...".format(arg)
        return arg.capitalize()