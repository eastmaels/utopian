import datetime
import pprint

from pymongo import MongoClient
from utopian import utopian_client

client = MongoClient()
db = client.utopian


def update_moderators():
    print(f"{datetime.datetime.now()} - Updating moderators.")
    moderators = db.moderators
    current_moderators = utopian_client.get_moderators()

    if not current_moderators:
        time = datetime.datetime.now()
        print(f"{time} - Could not update moderators.")
        return

    db.moderators.drop()
    moderators.insert_many(current_moderators)

def status_converter(status):
    if status == "any":
        return "approved"
    else:
        return status


def status_parameter(status):
    if status == "any":
        return {"moderator.flagged": False}
    elif status == "flagged":
        return {"moderator.flagged": True}
    elif status == "pending":
        return {"moderator": None}


def update_posts(status, force_complete=False):
    posts = db.posts
    post_status = status_converter(status)
    count = posts.find(status_parameter(status)).count()
    time = datetime.datetime.now()
    print(f"{time} - Updating {post_status} posts.")
    time = datetime.datetime.now()
    print(f"{time} - {count} {post_status} posts in the database.")
    if count == 0 or force_complete:
        utopian_client.get_posts(status, update=False)
    else:
        utopian_client.get_posts(status, update=True)

    added = posts.find(status_parameter(status)).count() - count
    time = datetime.datetime.now()
    print(f"{time} - {added} posts were added.")


def main():
    update_moderators()
    update_posts("any")
    update_posts("flagged")
    update_posts("pending", True)


def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()


if __name__ == '__main__':
    main()