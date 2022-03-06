import json
import os
from datetime import datetime, timedelta
import constants
import praw


# TODO: check id uniqueness
#       if comment id is unique for subreddit, then comment.permalink can be replaced with comment.id
# data.json is a dictionary: comment.permalink -> timestamp (first time seen negative)
def read_data():
    if not os.path.isfile("data.json"):
        return {}
    else:
        # TODO: recover parse failure
        with open("data.json") as outfile:
            return json.load(outfile, object_hook=object_hook)


def write_data(x):
    with open("data.json", "w") as outfile:
        json.dump(x, outfile, indent=2, default=default)


def default(obj):
    if isinstance(obj, datetime):
        return {"_isoformat": obj.isoformat()}
    raise TypeError("...")


def object_hook(obj):
    _isoformat = obj.get("_isoformat")
    if _isoformat is not None:
        return datetime.fromisoformat(_isoformat)
    return obj


def process_comment(item):
    if item.score < constants.SCORE_THRESHOLD:
        if (item.permalink in state) and (state[item.permalink] < timeAgo):
            print("Deleting:")
            # TODO: spam/remove it? test it
            # Also, lock the comment
            # item.mod.lock()
            # item.mod.remove(spam=True)
            del state[item.permalink]
        elif item.permalink not in state:
            print("Noting:")
            state[item.permalink] = datetime.now()

        print(item.score)
        print(item.permalink)
        print(item.body)
        print("---")
    # comment/topic went positive
    elif item.permalink in state:
        del state[item.permalink]


reddit = praw.Reddit("bot1")
subreddit = reddit.subreddit(constants.SUBREDDIT)

if __name__ == "__main__":
    state = read_data()
    print(state)

    for submission in subreddit.hot(limit=constants.N_HOT):
        process_comment(submission)

        print("Title: ", submission.title)
        print("Loading comments...")
        print(datetime.now())
        submission.comments.replace_more(limit=constants.N_COMMENTS)
        print("Comments loaded:")
        print(len(submission.comments))
        print(datetime.now())

        timeAgo = datetime.now() - timedelta(hours=constants.TIME_WINDOW_HOURS)

        not_deleted = (
            c
            for c in submission.comments.list()
            if c.collapsed_reason_code != "DELETED"
        )

        for comment in not_deleted:
            process_comment(comment)

        write_data(state)
        print("---------------------------------\n")
