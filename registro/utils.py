from django.contrib import admin


class TitledFilter(tuple):
    """
    Clase para colocar el nombre personalizado en los titulos de los filtros
    """

    def __new__(cls, title, field):
        class Wrapper(admin.FieldListFilter):
            def __new__(cls, *args, **kwargs):
                instance = admin.FieldListFilter.create(*args, **kwargs)
                instance.title = title
                return instance

        return field, Wrapper
