

from django.contrib.auth import get_user_model
from oauth2_provider import views


class TokenView(views.TokenView):

    def create_token_response(self, request):

        try:
            email = request.GET.copy().pop('email')[0]
            user = get_user_model().objects.get(email=email)
            self.change_email_to_username(request, user.username)
        except (KeyError, get_user_model().DoesNotExist):
            pass

        return super().create_token_response(request)

    @staticmethod
    def change_email_to_username(request, username):
        """
        Parameters used for request are for some reason stored in request.META['QUERY_STRING'] which is just url
        query string, we need to parse it, and replace email with username
        """
        a = []
        for pair in request.META['QUERY_STRING'].split("&"):
            items = pair.split('=')
            if items[0] == 'email':
                items[1] = username
                items[0] = "username"
            a.append('='.join(items))
        request.META['QUERY_STRING'] = "&".join(a)

