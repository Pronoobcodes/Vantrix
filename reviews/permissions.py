from rest_framework.permissions import BasePermission


class IsReviewerOrReadOnly(BasePermission):
    """
    Custom permission to only allow the reviewer of a review to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Write permissions are only allowed to the reviewer of the review.
        return obj.reviewer == request.user