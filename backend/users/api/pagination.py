from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    """Accepts the 'limit' parameter instead of the default value."""

    page_size_query_param = 'limit'
    page_size = 6
