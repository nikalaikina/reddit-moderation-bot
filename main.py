import json
import os
from datetime import datetime, timedelta

import praw


# TODO: check id uniqueness
# data.json is a dictionary: comment.permalink -> timestamp (first time seen negative)
def read_data():
    if not os.path.isfile("data.json"):
        return {}
    else:
        with open('data.json') as outfile:
            return json.load(outfile, object_hook=object_hook)


def write_data(x):
    with open("data.json", 'w') as outfile:
        json.dump(x, outfile, indent=2, default=default)


def default(obj):
    if isinstance(obj, datetime):
        return { '_isoformat': obj.isoformat() }
    raise TypeError('...')


def object_hook(obj):
    _isoformat = obj.get('_isoformat')
    if _isoformat is not None:
        return datetime.fromisoformat(_isoformat)
    return obj

reddit = praw.Reddit('bot1')
subreddit = reddit.subreddit("femalefashionadvice")

if __name__ == '__main__':
    state = read_data()
    print(state)

    for submission in subreddit.hot(limit=30):
        print("Title: ", submission.title)
        print("Loading comments...")
        print(datetime.now())
        submission.comments.replace_more(limit=5)
        print("Comments loaded:")
        print(len(submission.comments))
        print(datetime.now())

        hourAgo = (datetime.now() - timedelta(hours=1))

        # TODO: traverse tree
        # TODO: filter deleted out
        for comment in submission.comments:
            if comment.score < 0:
                if (comment.permalink in state) and (state[comment.permalink] < hourAgo):
                    # TODO: spam it
                    print("Deleting:")
                    del state[comment.permalink]
                elif comment.permalink not in state:
                    print("Noting:")
                    state[comment.permalink] = datetime.now()

                print(comment.score)
                print(comment.permalink)
                print(comment.body)
                print("---")
            # comment went positive
            elif comment.permalink in state:
                del state[comment.permalink]

        write_data(state)
        print("---------------------------------\n")
