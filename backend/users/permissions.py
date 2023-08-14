from rest_framework.permissions import IsAuthenticated, SAFE_METHODS


class AllowAnyGetPost(IsAuthenticated):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS) or (request.method == 'POST')


class CurrentUserOrAdmin(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.pk == user.pk or user.is_superuser
