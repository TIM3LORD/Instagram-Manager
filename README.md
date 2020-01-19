# Instagram-Manager

Instagram manager is designed to be a tool to automate management and cleaup operations on you instagram account.

Functions available right now:

1. List number of users not following you back
2. List usernames of users not following you back
3. Unfollow users not following you back
4. Check other similar pages to find potential followers

More function to be added in the future.

## Installation

This project uses the instagram_private_api by github user ping (https://github.com/ping/instagram_private_api)

Install this using pip
```pip install git+https://git@github.com/ping/instagram_private_api.git@1.6.0```
The above command might require git to be installed on your system so if you face a "git not found" error try installing git and re-run the command.

To run Instagram Manager use the following command
```python instagrammanager.py -u <username> -p <password> -settings <credentials.json>```

The settings argument is not required but it is important and used to store the auth cookie and avoid having to login for every api call since repeated logins can lead to instagram banning the account

This file will be created when you run the python script if it does not exist.

## This could lead to account bans. USE AT YOUR OWN RISK