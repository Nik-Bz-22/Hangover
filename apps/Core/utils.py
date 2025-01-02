menu = [
    {
        "name": "Home",
        "login_require": False,
        "path_name": "home",
        "always_show": True,
    },
    {
        "name": "View list of repository",
        "login_require": True,
        "path_name": "my_repositories",
        "always_show": False,

    },
    {
        "name": "Add new repository",
        "login_require": True,
        "path_name": "create_repository",
        "always_show": False,

    },
    {
        "name": "Create an account",
        "login_require": False,
        "path_name": "sign_up",
        "always_show": False,
    },
    {
        "name": "Log in",
        "login_require": False,
        "path_name": "log_in",
        "always_show": False,
    },
]



class DataMixin:
    page_title = None
    extra_context = {}


    def __init__(self):
        if self.page_title is not None:
            self.extra_context['title'] = self.page_title

        if 'menu' not in self.extra_context:
            self.extra_context['menu'] = menu

    def get_mixin_context(self, context, **kwargs):
        context['menu'] = menu
        context.update(kwargs)
        return context

