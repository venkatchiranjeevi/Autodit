from __future__ import with_statement
from django.conf import settings
from AutoditApp.core import get_session_value
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.utils.functional import SimpleLazyObject
# from AutoditApp.constants import Cognito
from AutoditApp.AWSCognito import Cognito
from AutoditApp.models import Roles

profiler = getattr(settings, 'PROFILER', {})
profiler_enabled = profiler.get('enabled', False)

if profiler_enabled:
    import pstats

    try:
        import cProfile
    except ImportError:
        import profile

    import io


def get_user(request):
    session_key = get_session_value(request)
    result, message = Cognito.verify_cognito_token(session_key)
    if result:
        claims = Cognito.claims_token(session_key)
        request._cached_user = Cognito.get_cognito_user(claims.get('sub')) or AnonymousUser()
    else:
        request._cached_user = AnonymousUser()
        request._cached_user.token_error = message
    return request._cached_user


class AutoDitAuthenticationMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        assert hasattr(request, 'session'), (
        "The Django authentication middleware requires session middleware "
        "to be installed. Edit your MIDDLEWARE%s setting to insert "
        "'django.contrib.sessions.middleware.SessionMiddleware' before "
        "'django.contrib.auth.middleware.ZestAuthenticationMiddleware'."
                                            ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")

        setattr(request, 'csrf_processing_done', True)
        user = get_user(request)
        request.user = user
        try:
            role_details = eval(user.role_id)
        except:
            role_details = None
        if role_details:
            role_details = eval(user.role_id)
            role_details = Roles.objects.filter(role_id__in=role_details).values('role_type', 'department_id')
            rolesWithDepartments = filter(lambda role: role.get('department_id') is not None , role_details)
            department_ids = [role.get('department_id') for role in rolesWithDepartments]
            isAdmin = False

            if len(department_ids) == 0:
                department_ids.append(-1)
            for role in role_details:
                if role.get('role_type') == 'ADMIN':
                    isAdmin = True
                    break
            request.user.isAdmin = isAdmin
            request.user.departments = department_ids


    def process_view(self, request, callback, callback_args, callback_kwargs):
        if profiler_enabled:
            self.profiler = cProfile.Profile()
            self.profiler.enable()

    def process_response(self, request, response):
        if profiler_enabled:
            self.profiler.disable()

            s = io.BytesIO()

            sortby = settings.PROFILER.get('sort', 'time')
            count = settings.PROFILER.get('count', None)
            # output = settings.PROFILER.get('output', ['console'])

            ps = pstats.Stats(self.profiler, stream=s).sort_stats(sortby).print_stats(count)
            # ps.print_stats()
            print (s.getvalue())
            # for output in settings.PROFILER.get('output', ['console', 'file']):
            #
            #     if output == 'console':
            #         print (s.getvalue())
            #
            #     if output == 'file':
            #         file_loc = settings.PROFILER.get('file_location', 'profiling_results.txt')
            #         with open(file_loc, 'a+') as file:
            #             counter = str(s.getvalue())
            #             file.write(counter)

        return response
