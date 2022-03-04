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
        # TODO: recover parse failure
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




def process_comment(item):
    if item.score < 0:
        if (item.permalink in state) and (state[item.permalink] < hourAgo):
            print("Deleting:")
            # TODO: spam it or remove? test it
            item.mod.remove(spam=True)
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


reddit = praw.Reddit('bot1')
subreddit = reddit.subreddit("femalefashionadvice")

if __name__ == '__main__':
    state = read_data()
    print(state)

    for submission in subreddit.hot(limit=100):
        process_comment(submission)

        print("Title: ", submission.title)
        print("Loading comments...")
        print(datetime.now())
        submission.comments.replace_more(limit=30)
        print("Comments loaded:")
        print(len(submission.comments))
        print(datetime.now())

        hourAgo = (datetime.now() - timedelta(hours=1))

        not_deleted = (c for c in submission.comments if c.collapsed_reason_code != 'DELETED')

        # TODO: traverse tree
        for comment in not_deleted:
            process_comment(comment)

        write_data(state)
        print("---------------------------------\n")
