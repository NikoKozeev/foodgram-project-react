from django.http import Http404


def get_user_from_context(context):
    """Get user from context."""
    try:
        request = context['request']
        user = request.user
        if not user.is_authenticated:
            raise Http404("User not authenticated")
    except KeyError:
        raise Http404("Request not found in context")
    return user
