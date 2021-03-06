import json
import codecs
import datetime
import os.path
import logging
import argparse
import time
import wget
from random import randrange
try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('SAVED: {0!s}'.format(new_settings_file))


if __name__ == '__main__':

    logging.basicConfig()
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)

    # Example command:
    # python examples/savesettings_logincallback.py -u "yyy" -p "zzz" -settings "test_credentials.json"
    parser = argparse.ArgumentParser(description='login callback and save settings demo')
    parser.add_argument('-settings', '--settings', dest='settings_file_path', type=str, required=True)
    parser.add_argument('-u', '--username', dest='username', type=str, required=True)
    parser.add_argument('-p', '--password', dest='password', type=str, required=True)
    parser.add_argument('-debug', '--debug', action='store_true')

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    print('Client version: {0!s}'.format(client_version))

    device_id = None
    try:

        settings_file = args.settings_file_path
        if not os.path.isfile(settings_file):
            # settings file does not exist
            print('Unable to find file: {0!s}'.format(settings_file))

            # login new
            api = Client(
                args.username, args.password,
                on_login=lambda x: onlogin_callback(x, args.settings_file_path))
        else:
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=from_json)
            print('Reusing settings: {0!s}'.format(settings_file))

            device_id = cached_settings.get('device_id')
            # reuse auth settings
            api = Client(
                args.username, args.password,
                settings=cached_settings)

    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

        # Login expired
        # Do relogin but use default ua, keys and such
        api = Client(
            args.username, args.password,
            device_id=device_id,
            on_login=lambda x: onlogin_callback(x, args.settings_file_path))

    except ClientLoginError as e:
        print('ClientLoginError {0!s}'.format(e))
        exit(9)
    except ClientError as e:
        print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
        exit(9)
    except Exception as e:
        print('Unexpected Exception: {0!s}'.format(e))
        exit(99)

    # Show when login expires
    cookie_expiry = api.cookie_jar.auth_expires
    print('Cookie Expiry: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))


    class User(object):
        username = ""
        userid =""
        profile_img = ""
        following = ""
        followers = ""
        isPrivate =""
        isVerified = ""
        fullName = ""
        bio =""
        isBusiness = ""
        taggedin = ""
        posts =""

        def __init__ (self, userid,username,profile_img,following,followers,isPrivate,isVerified,fullName,bio,isBusiness,taggedin,posts):
            self.userid=userid
            self.username=username
            self.profile_img=profile_img
            self.following=following
            self.followers=followers
            self.isPrivate=isPrivate
            self.isBusiness=isBusiness
            self.isVerified=isVerified
            self.fullName=fullName
            self.bio= bio
            self.taggedin=taggedin
            self.posts=posts

        def to_String(self):
            print("userid : "+str(self.userid))
            print("username : "+self.username)
            print("profile image : "+self.profile_img)
            print("Full Name : "+self.fullName)
            print("Biography : "+self.bio)
            print("followers : "+str(self.followers))
            print("following : "+str(self.following))
            print("post count : "+str(self.posts))
            print("tagged in count : "+str(self.taggedin))
            print("isPrivate : "+str(self.isPrivate))
            print("isVerified : "+str(self.isVerified))
            print("isBusiness : "+str(self.isBusiness))


    def getUserDetails(username):
        result=api.username_info(username)
        user= User(result["user"]["pk"],result["user"]["username"],result["user"]["hd_profile_pic_url_info"]["url"],result["user"]["following_count"],result["user"]["follower_count"],result["user"]["is_private"],result["user"]["is_verified"],result["user"]["full_name"],result["user"]["biography"],result["user"]["is_business"],result["user"]["usertags_count"],result["user"]["media_count"])
        return user
    
# get followers and following return in the format userid*ljc*username to avoid more api calls to get username
    delim="*ljc*"

    def get_followers(userid):
        followers = []
        followers_id = []
        rank_token = Client.generate_uuid()
        res=api.user_followers(userid,rank_token)
        
        followers.extend(res.get("users",[]))
        next_max_id=res.get("next_max_id")
        while next_max_id:
            res=api.user_followers(userid,rank_token,max_id=next_max_id)
            followers.extend(res.get("users",[]))
            next_max_id=res.get("next_max_id")
        for follow in followers:
            followers_id.append(str(follow["pk"])+delim+follow["username"])
        return followers_id

    def get_following(userid):
        following = []
        following_id = []
        rank_token = Client.generate_uuid()
        res=api.user_following(userid,rank_token)
        
        following.extend(res.get("users",[]))
        next_max_id=res.get("next_max_id")
        while next_max_id:
            res=api.user_following(userid,rank_token,max_id=next_max_id)
            following.extend(res.get("users",[]))
            next_max_id=res.get("next_max_id")
        for follow in following:
            following_id.append(str(follow["pk"])+delim+follow["username"])
        return following_id

    def get_non_followers(userid):
        non_followers = []
        following = get_following(userid)
        followers = get_followers(userid)

        for follow in following:
            if follow not in followers:
                non_followers.append(follow)
        
        return non_followers

    def get_private_non_followers(userid):
        non_followers = []
        following = get_following(userid)
        followers = get_followers(userid)

        start=True
        for follow in following:

            # if "tarun_sibal" in follow and start == False:
            #     start=True
                

            if follow not in followers and start:
                if getUserDetails(follow.split(delim)[1]).isPrivate == True:
                    print(follow.split(delim)[1])
                    non_followers.append(follow)
        
        return non_followers

    def get_usernames_from_userids(userid):
        usernames=[]
        for user in userid:
            username= api.user_info(user)["user"]["username"]
            # print(username)
            usernames.append(username)
            # time.sleep(randrange(1,2))
        return usernames

    def unfollow(users):
        # Explicitly limit the number of people unfollowed at a time to avoid hitting instagrams limit
        limit=150
        for user in users:
            if limit == 0:
                break
            user_=int(user.split(delim)[0])
            print(user_)
            res = api.friendships_destroy(user_,"")
            limit = limit-1
            if(res["status"] != "ok"):
                failed.append(user)
                print("Failed to unfollow "+user.split(delim)[1])
            else:
                print("Unfollowed "+user.split(delim)[1])
            
            time.sleep(randrange(10,15))

        return failed
    
    def findPeopleToFollow(account):
        f= open(account+".txt","a")
        account=getUserDetails(account)
        self_following= get_following(26714596870)
        account_followers=get_followers(account.userid)
        print(account.username+" has "+str(len(account_followers))+" followers")
        i=1
        for follower in account_followers:
            if(i<190):
                print("skipping "+str(i))
                i=i+1
                continue
            if follower in self_following:
                continue
            follower=getUserDetails(follower.split(delim)[1])
            if(follower.isPrivate):
                if(follower.following > follower.followers):
                    print(follower.username+" is PRIVATE and following "+str(follower.following)+" and has "+str(follower.followers)+" followers")
                    f.write(follower.username+" is PRIVATE and following "+str(follower.following)+" and has "+str(follower.followers)+" followers\n")
                    f.flush()
           # time.sleep(1)
        f.close()

    def getStory(uname):
        user = getUserDetails(uname)
        story = api.user_story_feed(user.userid)
        # print(story)
        folder_name = uname+"-"+ str(time.time())
        os.mkdir(folder_name)
        for item in story["reel"]["items"]:
            # if(item["media_type"]==1):
            #     url = item["image_versions2"]["candidates"][0]["url"]
            # else:
            #     url = item["video_versions"]["candidates"][0]["url"]
            if "video_versions" in item:
                url = item["video_versions"][0]["url"]
            else:
                for img in item["image_versions2"]:
                    key = img
                    # url = img[0]["url"]
                url = item["image_versions2"][key][0]["url"]

            print(url)
            
            wget.download(url,out=folder_name)
            print("Downloaded")


    def getUserPosts(uname):
        user = getUserDetails(uname)
        posts = api.user_feed(user.userid)
        folder_name = uname+"-posts-"+ str(time.time())
        os.mkdir(folder_name)
        for item in posts["items"]:
            print(item["taken_at"])
            if "image_versions2" in item:
                url = item["image_versions2"]["candidates"][0]["url"]
                print(url)
                wget.download(url,out=folder_name)
            if "carousel_media" in item:
                for media in item["carousel_media"]:
                    if "image_versions2" in media:
                        url = media["image_versions2"]["candidates"][0]["url"]
                        print(url)
                        wget.download(url,out=folder_name)
                    if "video_versions" in media:
                        url = media["video_versions"][0]["url"]
                        print(url)
                        wget.download(url,out=folder_name)
            if "video_versions" in item:
                url = item["video_versions"][0]["url"]
                print(url)
                wget.download(url,out=folder_name)


        


    userid = getUserDetails("divinepalate").userid
    print("Instagram Manager\n")
    
    while True:
        print("1. Number of users not following back")
        print("2. Usernames of users not following back")
        print("3. Unfollow users not following back")
        print("4. Find people to follow by checking other accounts")
        print("5. Usernames of private users not following back")
        print("6. Download user story")
        print("7. Download latest user posts")
        # add more functions here
        print("Ctrl +c to quit")

        choice = input ("Enter your choice: ")
        if choice == "1":
            print(len(get_non_followers(userid)))
        if choice == "2":
            non_followers = get_non_followers(userid)
            for non in non_followers:
                print(non.split(delim)[1])
            print(str(len(non_followers))+" users do not follow you back")
        if choice == "3":
            print("Only 150 users will be unfollowed at a time to avoid hitting instagram's unfollowing limit")
            failed = unfollow(get_non_followers(userid)) 
            if failed == []:
                print( "Unfollowed all successfully")
        if choice == "4":
            username = input ("Enter the username of the account you want to check: ")
            findPeopleToFollow(username)
        if choice == "5":
            non_followers = get_private_non_followers(userid)
            # for non in non_followers:
            #     print(non.split(delim)[1])
            print(str(len(non_followers))+" private users do not follow you back")
        if choice == "6":
            username = input ("Enter the username of the account you want to download story: ")
            getStory(username)
        if choice == "7":
            username = input ("Enter the username of the account you want to view posts: ")
            getUserPosts(username)
            

    