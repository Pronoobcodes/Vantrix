from django.db.models import Avg
from django.db.models import Count

from .models import Review


def get_average_rating_for_user(user):
    """
    Calculate the average rating for a given user based on reviews received.
    """
    average_rating = Review.objects.filter(reviewed_user=user).aggregate(Avg('rating'))['rating__avg']
    return average_rating if average_rating is not None else 0


def get_rating_breakdown(user):
    """
    Get the breakdown of ratings for a given user based on reviews received.
    Returns a dictionary with counts of each rating (1 to 5).
    """
    rating_counts = Review.objects.filter(reviewed_user=user).values('rating').annotate(count=Count('rating'))
    breakdown = {i: 0 for i in range(1, 6)}  # Initialize counts for ratings 1 to 5

    for entry in rating_counts:
        breakdown[entry['rating']] = entry['count']

    return breakdown


def get_review_stats(user):

    reviews = Review.objects.filter(reviewed_user=user)

    average = (reviews.aggregate(avg=Avg("rating"))["avg"] or 0)

    return {
        "average_rating": round(
            average,
            2
        ),
        "total_reviews": reviews.count(),
        "five_star": reviews.filter(
            rating=5
        ).count(),
        "four_star": reviews.filter(
            rating=4
        ).count(),
        "three_star": reviews.filter(
            rating=3
        ).count(),
        "two_star": reviews.filter(
            rating=2
        ).count(),
        "one_star": reviews.filter(
            rating=1
        ).count(),
    }
