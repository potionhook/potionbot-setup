#!/usr/bin/env python3

# This script automatically sets up Steam avatars, nicknames, and gathers the SteamID32 for bots.
# Change make_commands to False if you wish to get just the SteamID32, instead of Cathook's change playerstate command
# You do not have to "set up" a steam profile on each account for this to work, evidently.
# Simply copy your accounts.txt and bot-profile.jpg here and run: ./auto-profile.py
# Image format can be PNG, this script just expects the filename to be .jpg (avatars doesnt work)
# Thanks to Twojapies for reupload

# Make sure you install dependencies first:
# pip3 install -U steam[client]

import json
import time
import random
import steam.client

f = open('accounts.txt', 'r')
data = f.read()
f.close()

data = data.replace('\r\n', '\n')
accounts = data.split('\n')
accounts = [account for account in accounts if account.strip()]  # we don't want empty strings.

profile = open('avatar.png', 'rb')
nickname = 'put your nickname here'

enable_debugging = False
enable_extra_info = False
enable_avatarchange = False #broken
enable_namechange = True
enable_nameclear = False
enable_set_up = False
enable_gatherid32 = True
dump_response = False
make_commands = True
force_sleep = False

random_chars = [ '็', '่', '๊', '๋', '์', 'ู']  # Modify this list as needed

def debug(message):
    if enable_debugging:
        print(message)

def extra(message):
    if enable_extra_info:
        print(message)

def insert_random_chars(name, chars, num_insertions):
    name_list = list(name)
    for _ in range(num_insertions):
        pos = random.randint(0, len(name_list))
        char = random.choice(chars)
        name_list.insert(pos, char)
    return ''.join(name_list)

if enable_gatherid32:
    open('steamid32.txt', 'w').close()  # Erase any previous contents
    id_file = open('steamid32.txt', 'a')  # Open the file as append

for index, account in enumerate(accounts):
    username, password = account.split(':')
    print(f'Logging in as user #{index + 1}/{len(accounts)} ({username})...')

    client = steam.client.SteamClient()
    eresult = client.login(username, password=password)
    status = 'OK' if eresult == 1 else 'FAIL'
    print(f'Login status: {status} ({eresult})')
    if status == 'FAIL':
        raise RuntimeError(
            'Login failed; bailing out. See https://steam.readthedocs.io/en/stable/api/steam.enums.html#steam.enums'
            '.common.EResult for the relevant error code.')

    print(f'Logged in as: {client.user.name}')
    print(f'Community profile: {client.steam_id.community_url}')
    extra(f'Last logon (UTC): {client.user.last_logon}')
    extra(f'Last logoff (UTC): {client.user.last_logoff}')

    if enable_gatherid32:
        id32 = str(client.steam_id.as_32)
        if make_commands:
            id_file.write(f'cat_pl_add_id {id32} CAT\n')
            print('Saved the SteamID32 as a Cathook change playerstate command.')
        else:
            id_file.write(f'{id32}\n')
            print('Saved the SteamID32 as raw.')

    if enable_namechange:
        modified_nickname = insert_random_chars(nickname, random_chars, 3)  # Insert 3 random characters
        time.sleep(5)  # Needed, since Steam refuses to change status if we do it too soon
        client.change_status(persona_state=1, player_name=modified_nickname)
        print(f'Changed Steam nickname to "{modified_nickname}"')

    if enable_avatarchange or enable_nameclear or enable_set_up:
        print('Getting web_session...')
        session = client.get_web_session()
        if session is not None:
            debug(f'session.cookies: {session.cookies}')

            if enable_avatarchange:
                url = 'https://steamcommunity.com/actions/FileUploader'
                id64 = client.steam_id.as_64  # type int
                data = {
                    'MAX_FILE_SIZE': '1048576',
                    'type': 'player_avatar_image',
                    'sId': str(id64),
                    'sessionid': session.cookies.get('sessionid', domain='steamcommunity.com'),
                    'doSub': '1',
                }
                post_cookies = {
                    'sessionid': session.cookies.get('sessionid', domain='steamcommunity.com'),
                    'steamLoginSecure': session.cookies.get('steamLoginSecure', domain='steamcommunity.com')
                }

                print('Setting profile picture...')

                r = session.post(url=url, params={'type': 'player_avatar_image', 'sId': str(id64)},
                                files={'avatar': profile},
                                data=data, cookies=post_cookies)
                content = r.content.decode('ascii')
                if dump_response:
                    print(f'response: {content}')
                if not content.startswith('<!DOCTYPE html'):
                    response = json.loads(content)
                    if 'message' in response:
                        raise RuntimeError(f'Error setting profile: {response["message"]}')

            if enable_nameclear:
                print('Clearing nickname history...')
                id64 = client.steam_id.as_64
                r = session.post(f'https://steamcommunity.com/my/ajaxclearaliashistory/',
                                 data={'sessionid': session.cookies.get('sessionid', domain='steamcommunity.com')},
                                 cookies={'sessionid': session.cookies.get('sessionid', domain='steamcommunity.com'),
                                          'steamLoginSecure': session.cookies.get('steamLoginSecure',
                                                                                  domain='steamcommunity.com')})

            if enable_set_up:
                print('Setting up community profile...')
                r = session.post(f'https://steamcommunity.com/my/edit?welcomed=1',
                                 data={'sessionid': session.cookies.get('sessionid', domain='steamcommunity.com')},
                                 cookies={'sessionid': session.cookies.get('sessionid', domain='steamcommunity.com'),
                                          'steamLoginSecure': session.cookies.get('steamLoginSecure',
                                                                                  domain='steamcommunity.com')})

        else:
            print("Failed to create a session. Check your authentication or network.")

    print('Done; logging out.')
    client.logout()

    # Seek to the beginning of the profile image file; reuse the file
    profile.seek(0)

    # Spacing between accounts
    print()

    # Only pause if we're changing avatars or setting up the community profile, and we're not at the last account,
    # we have less than or equal to 10 accounts in total, or force_sleep is set to True
    if ((enable_avatarchange or enable_set_up) and (index + 1 != len(accounts) or len(accounts) <= 10)) or force_sleep:
        # For file avatars, no more than 10 avatars per 5 minutes from each IP address
        time.sleep(31)

if enable_gatherid32:
    id_file.close()

profile.close()

print('Done.')
