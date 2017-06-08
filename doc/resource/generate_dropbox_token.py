import sys
import webbrowser

import dropbox


def generate_token(app_key, app_secret):
    '''Generate access token for Dropbox Core API.

    Get your app key and secret from the Dropbox developer website
    '''

    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(
        app_key,
        app_secret
    )

    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print '1. Go to: ' + authorize_url
    print '2. Click "Allow" (you might have to log in first)'
    print '3. Copy the authorization code.'

    webbrowser.open_new(authorize_url)

    code = raw_input('Enter the authorization code here: ').strip()

    # This will fail if the user enters an invalid authorization code
    access_token, user_id = flow.finish(code)

    print ''
    print 'Generated access token'
    print '----------------------'
    print access_token
    print '----------------------'

    return access_token


if __name__ == '__main__':
    if not len(sys.argv) == 3:
        sys.exit('Usage: python generate_dropbox_token.py <app_key> <app_secret>')

    app_key = sys.argv[1]
    app_secret = sys.argv[2]

    access_token = generate_token(app_key, app_secret)
    client = dropbox.client.DropboxClient(access_token)
    print ''
    print 'Linked account:', client.account_info().get('display_name')
    print ''
