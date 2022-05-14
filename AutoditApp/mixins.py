from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class AuthMixin(APIView):
    """
    Session validation : by django default is_authenticated()
    """
    default_message = "Incorrect authentication credentials."

    def dispatch(self, request, *args, **kwargs):
        message = None
        if IsAuthenticated().has_permission(request, self):
            if getattr(request.user, "markedfordeletion", True):
                message = "Account disabled. Contact administrator"
        elif hasattr(request.user, 'token_error'):
            message = request.user.token_error
        else:
            message = self.default_message
        if message:
            return JsonResponse({"detail": message}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return super(AuthMixin, self).dispatch(request, *args, **kwargs)
