from django.utils.deprecation import MiddlewareMixin
from .models import User


class Auth0UserSyncMiddleware(MiddlewareMixin):
    """
    Middleware to sync Auth0 user data with local database
    Updates session with user role and profile information
    """

    def process_request(self, request):
        # Get Auth0 user data from session
        auth0_user = request.session.get('user')

        if auth0_user and isinstance(auth0_user, dict):
            # Extract Auth0 user ID from userinfo
            auth0_id = auth0_user.get('userinfo', {}).get('sub')

            if auth0_id:
                try:
                    # Get or create user in local database
                    user = User.objects.get(auth0_id=auth0_id)

                    # Update session with user data from database
                    request.session['user']['role'] = user.role
                    request.session['user']['onboarding_complete'] = user.onboarding_complete
                    request.session['user']['user_id'] = user.id
                    request.session['user']['username'] = user.username
                    request.session['user']['full_name'] = user.get_full_name()

                    # Add teacher-specific data
                    if user.is_teacher and hasattr(user, 'teacher_profile'):
                        request.session['user']['verification_status'] = user.teacher_profile.verification_status
                        request.session['user']['is_verified'] = user.teacher_profile.is_verified

                    # Mark session as modified to save changes
                    request.session.modified = True

                except User.DoesNotExist:
                    # User exists in Auth0 but not in our database yet
                    # This will be handled by the callback view
                    pass

        return None
