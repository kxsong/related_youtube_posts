import praw
import dateutil.relativedelta
import HTMLParser
import urlparse
import datetime

def getcanonical(id):
    """the 'canonical' url for a youtube video"""
    return 'http://www.youtube.com/watch?v='+id[:11]

def geturls(id):
    return [getcanonical(id),
    'http://www.youtu.be/'+id[:11],
    'https://www.youtube.com/watch?v='+id[:11],
    'http://www.youtube.com/watch?feature=player_embedded&v='+id[:11],
    'http://www.youtube.com/watch?feature=player_detailpage&v='+id[:11],
    'http://www.youtube.com/watch?v='+id[:11]+'&feature=youtu.be',
    'http://www.youtube.com/watch?v='+id[:11]+'&feature=share',
    'http://www.youtube.com/watch?v='+id[:11]+'&feature=related', #rare
    'http://www.youtube.com/watch?v='+id[:11]+'&feature=plcp', #2nd rarest
    'http://www.youtube.com/watch?v='+id[:11]+'&feature=youtube_gdata_player']

def humantime(timestamp):
    dt1 = datetime.datetime.now()
    dt2 = datetime.datetime.fromtimestamp(timestamp)
    rd = dateutil.relativedelta.relativedelta(dt1, dt2)
    if rd.years >= 1:
        return "%d ^^years" % (rd.years)
    if rd.months >= 1:
        return "%d ^^months" % (rd.months)
    if rd.days >= 1:
        return "%d ^^days" % (rd.days)
    if rd.hours >= 1:
        return "%d ^^hours" % (rd.hours)
    return "%d ^^minutes" % (rd.minutes)


if __name__ == "__main__":
    f1 = open('./urls-canonical.txt', 'a')
    f2 = open('./urls-not-canonical.txt', 'a')
    f3 = open('./urls-other.txt', 'a')
    f4 = open('./post-ids.txt', 'r+')
    post_ids = f4.readlines()
    for post_id in post_ids:
        post_id.strip()
    h = HTMLParser.HTMLParser()
    r = praw.Reddit(user_agent = '/u/yt_related_posts bot by /u/kxsong')
    r.login(username="related_yt_posts")
    #domain/new does not work when not logged in. also must visit http://www.reddit.com/domain/youtube.com/new/?sort=new first
    posts = r.get_content(url="http://www.reddit.com/domain/youtube.com/new/", limit=None)
    for post in posts:
        url = h.unescape(post.url).split('#')[0] #remove anchor
        query = urlparse.parse_qs(urlparse.urlparse(url).query)
        if query.has_key('v'): #is it an actual video, and not some other youtube page?
            id = query['v'][0]
            if post.id not in post_ids: #don't look again
                post_ids += post.id
                print >>f4, post.id
                comment = """these matching videos in /r/%s may be of interest:

Title | ^^comments | ^^score | ^^age
:--|:--|:--|:--
""" % post.subreddit.display_name
                altcount = 0
                print("/r/"+post.subreddit.display_name + ": " + post.title + ": " + url+"\n")
                for alt_url in geturls(id):
                    #print("unescaped alt: " + h.unescape(alt_url))
                    if h.unescape(alt_url) != url: #same video, different url
                        alts = r.get_info(url=alt_url)
                        for alt_post in alts:
                            if (alt_post.score > 1 or alt_post.num_comments > 1) and post.subreddit.display_name == alt_post.subreddit.display_name:
                                altcount += 1
                                comment+=("["+alt_post.title+"]("+alt_post.permalink+")|"+str(alt_post.num_comments)+"|"
                                +str(alt_post.score)+"|"+humantime(alt_post.created_utc)+"\n")
                if altcount >= 1: #tell user
                    print(comment)
                    alt_post.comments[0].reply(comment)
                canonicalurl = getcanonical(id)
                if url != canonicalurl:
                    print >>f2, url
                else:
                    print >>f1, url
        else:
            print >>f3, url