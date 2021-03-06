from .page import FacebookPage
import argparse
from datetime import datetime
import asyncio
import csv
        

POSTS_TXT_HEAD = [
    "id", "url", "timestamp", "message", "reactions_count",
    "comments_count", "shares_count"
]

async def getFacebookPagePosts(pageName, afterDate):
    async with FacebookPage(pageName, afterDate) as fb:
        await fb.fetchAll()
        return fb.posts

def writePostsToTxt(posts, filename, mode):
    if mode not in ("w", "a", "wt", "at"):
        raise ValueError(f"mode {mode} invalid.")
    with open(filename, mode) as fh:
        writer = csv.DictWriter(
            fh, POSTS_TXT_HEAD, quoting=csv.QUOTE_NONNUMERIC
        )
        if mode in ("w", "wt"):
            writer.writeheader()
        for post in posts:
            writer.writerow({
                "id": post["id"],
                "url": post["url"],
                "timestamp": datetime.strftime(post["datetime"], "%Y-%m-%d"),
                "message": post["postMsg"],
                "reactions_count": post["reactionsCount"],
                "comments_count": post["commentsCount"],
                "shares_count": post["sharesCount"]
            })

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--pagename", type=str, help="Facebook Page Name"
    )
    parser.add_argument(
        "-i", "--input-txt", type=str,
        help="Input list of Facebook names. Must be one pagename each line."
    )
    parser.add_argument(
        "-d", "--date", type=str, default="1970-01-01", 
        help="""The datetime cutoff to retrieve posts. Must be year-month-day, 
        example: 2019-01-01"""
    )
    parser.add_argument(
        "-o", "--output-file", type=str, help="Output filename"
    )
    return parser.parse_args()

async def main():
    args = parse_args()
    date = datetime.strptime(args.date, "%Y-%m-%d")
    if args.input_txt:
        with open(args.intput_txt, "rt") as fh:
            i = 0
            for line in fh:
                if i == 0:
                    mode = "wt"
                    i += 1
                else:
                    mode = "a"
                posts = await getFacebookPagePosts(line.rstrip(), date)
                writePostsToTxt(posts, args.output_file, mode)
    else:
        if args.pagename is None:
            raise ValueError("Either -n or -i must be given.")
        posts = await getFacebookPagePosts(args.pagename, date)
        writePostsToTxt(posts, args.output_file, "wt")

def mainWrapper():
    asyncio.run(main())

if __name__ == '__main__':
    mainWrapper()
    
