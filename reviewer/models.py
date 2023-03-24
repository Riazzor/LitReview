from django.conf import settings
from django.db import models
from django.dispatch import receiver
import os


class Ticket(models.Model):
    title = models.CharField('Titre', max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    image = models.ImageField(null=True, blank=True, upload_to='images/')
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
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='is_following')
    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='is_followed_by',
    )

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


@receiver(models.signals.post_delete, sender=Ticket)
def delete_image_on_ticket_delete(sender, instance, **kwargs):
    """
    Delete image when ticket is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=Ticket)
def update_image_on_ticket_update(sender, instance, **kwargs):
    """
    Deletes old image from filesystem
    when corresponding `Ticket` object is updated
    with new image.
    """
    if not instance.pk:
        return False

    try:
        old_image = sender.objects.get(pk=instance.pk).image
        if not old_image:
            # Rare case when image doesn't exist but no exception raised.
            return False
    except sender.DoesNotExist:
        return False

    new_image = instance.image
    if not old_image == new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)
