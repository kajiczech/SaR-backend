

from django.contrib.auth import get_user_model
from oauth2_provider import views


class TokenView(views.TokenView):

    def create_token_response(self, request):

        # In some requests, the token is in request.POST, in others in request.GET
        try:
            post_data = request.POST.copy()
            email = post_data.pop('email')[0]
            try:
                user = get_user_model().objects.get(email=email)
                username = user.username
            except get_user_model().DoesNotExist:
                username = ''

            post_data["username"] = username
            request.POST = post_data
        except KeyError:
            try:
                email = request.GET.copy().pop('email')[0]

                try:
                    user = get_user_model().objects.get(email=email)
                    username = user.username
                except get_user_model().DoesNotExist:
                    username = ''

                self.change_email_to_username(request, username)
            except KeyError:
                pass

        return super().create_token_response(request)

    @staticmethod
    def change_email_to_username(request, username):
        """
        Parameters used for request are for some reason used from request.META['QUERY_STRING'] which is just url
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

