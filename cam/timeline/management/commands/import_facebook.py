from django.core.management.base import BaseCommand


def dig(collection, *args):
    """
    Look into a series of hashes and lists, pulling out the value at that
    location or None if it is an invalid path.
    """
    cur = collection
    for arg in args:
        if cur is None:
            return None
        try:
            cur = cur[arg]
        except (KeyError, IndexError):
            return None
    return cur


def ready_for_import(post):
    return (
        post.get("title")
        and (
            post["title"].endswith("updated his status.")
            or post["title"].endswith("shared a link.")
        )
    ) and dig(post, "data", 0, "post")


def ready_for_photo_import(post):
    import re

    attachments = dig(post, "attachments", 0, "data") or []
    if not attachments:
        return False

    uris = [dig(a, "media", "uri") or "" for a in attachments]

    for uri in uris:
        if not re.search(r"((Timeline|Instagram)Photos|MobileUploads)", uri):
            return False

    return True


def scrub_name_links(text):
    if text is None:
        return None

    import re

    return re.sub(r"@\[\d+:\d+:(\w+)\]", r"\1", text)


class Command(BaseCommand):
    help = "Import data from Facebook"

    def add_arguments(self, parser):
        parser.add_argument(
            "import_dir", help="Directory containing Facebook JSON export"
        )

    def handle(self, *args, **options):
        import os.path
        import json
        from datetime import datetime, timezone
        from django.core.files import File
        from timeline.models import Post, Photo

        def fbphoto_to_post(fbpost):
            post = Post()
            post.body = scrub_name_links(dig(fbpost, "data", 0, "post"))
            post.data = {"import": "facebook"}
            post.posted_at = datetime.fromtimestamp(fbpost["timestamp"], timezone.utc)
            post.save()

            attachments = dig(fbpost, "attachments", 0, "data")
            for attachment in attachments:
                create_photo(post, attachment)
            return post

        def create_photo(post, attachment):
            photo_uri = dig(attachment, "media", "uri")
            import_dir = options["import_dir"]
            photo_path = os.path.join(import_dir, photo_uri)
            description = scrub_name_links(dig(attachment, "media", "description"))
            photo = Photo(post=post)
            if not post.body == description:
                photo.caption = description
            photo.image.save(os.path.basename(photo_path), File(open(photo_path, "rb")))
            photo.save()
            return photo

        def fbpost_to_post(fbpost):
            if not ready_for_import(fbpost) and ready_for_photo_import(fbpost):
                return fbphoto_to_post(fbpost)
            post = Post()
            post.body = scrub_name_links(dig(fbpost, "data", 0, "post"))
            post.data = {"import": "facebook"}
            link = dig(fbpost, "attachments", 0, "data", 0, "external_context", "url")
            if link:
                post.data["link"] = link
            post.posted_at = datetime.fromtimestamp(fbpost["timestamp"], timezone.utc)
            post.save()
            return post

        Post.objects.filter(data__import="facebook").delete()
        import_dir = options["import_dir"]
        posts_filename = os.path.join(import_dir, "posts", "your_posts.json")
        with open(posts_filename) as fh:
            posts_json = fh.read()

        posts = json.loads(posts_json)["status_updates"]
        i = 0
        for post in posts:
            if ready_for_import(post) or ready_for_photo_import(post):
                i += 1
                fbpost_to_post(post)

        print(f"{i} imported")
