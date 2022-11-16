# from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models


class Ticket(models.Model):
    title = models.CharField('Titre', max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    class Ratings(models.IntegerChoices):
        TRASH = 0
        VERY_BAD = 1
        BAD = 2
        MEEEE = 3
        GOOD = 4
        PERFECT = 5

    # ticket.reviews will give us list of review which ticket corresponds to the current ticket.
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=Ratings.choices)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    headline = models.CharField('Titre', max_length=128)
    body = models.TextField('Commentaire', max_length=8192, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ticket', 'user', )  # a user can't make 2 reviews of the same ticket


class UserFollows(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed_by')

    class Meta:
        # ensures we don't get multiple UserFollows instances
        # for unique user-user_followed pairs
        unique_together = ('user', 'followed_user', )
        constraints = [
            models.CheckConstraint(
                name="cant_follow_self",
                check=~models.Q(user=models.F("followed_user")),
            ),
        ]
