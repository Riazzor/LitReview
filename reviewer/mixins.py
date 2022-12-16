from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class AnonymousMixins(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated:
            return False
        return True

    def handle_no_permission(self):
        return redirect('reviewer:flux')
