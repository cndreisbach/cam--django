from django.shortcuts import render
from django.db import connection
from datetime import datetime, timedelta
from itertools import groupby
from .models import Post


def timeline(request):
    offset = int(request.GET.get("offset", 0))
    limit = int(request.GET.get("limit", 10))
    start_date_str = request.GET.get("start", "")

    posts = Post.objects.all()
    if start_date_str:
        start_date = datetime.strptime("%Y-%m-%d", start_date_str)
        start_date += timedelta(1)
        posts = posts.filter(posted_at__lte=start_date)

    total = posts.count()
    posts = posts[offset : offset + limit]

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT(DATE_TRUNC('month', posted_at)) AS year_month 
            FROM timeline_post ORDER BY year_month DESC
            """
        )
        months = cursor.fetchall()
    months = [year_month[0] for year_month in months]
    months_by_year = groupby(months, lambda month: month.year)
    return render(
        request,
        "timeline/posts.html",
        {
            "total": total,
            "posts": posts,
            "months_by_year": months_by_year,
            "start_date_str": start_date_str,
        },
    )

