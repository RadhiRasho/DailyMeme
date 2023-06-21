# Daily Meme

Creates a System Tray Icon (Notification) which sends out an email daily at 10:00 AM with a meme fetched using the [this api](https://github.com/D3vd/Meme_Api) from reddit and passes it to the email body, Thank you [Dev Daksan](https://github.com/D3vd).

The System Tray Icon, when right clicked has quite a few options

For testing purposes, I've added a "Testing" mode into it, read more about it down below.

It also contains a `Switch Sub Reddits` context menu list which, yup you guessed it, allows you to list out a few different sub reddits to allow, I'm partial to the `r/ProgrammerHumor` subreddit. The list is currently hardcoded, but when I have the time I'll probably make that an envrionment variable as well.



## Requirements:
* Few packages are necessary for this to run which can be found in the [setup.py](setup.py) file
* You'll also need an SMTP Server to actually sendout the emails, set the `MAILING_SERVER` variable in a .env file to pass in your server
* `SEND_TO_LIST` is a list of recipients of the email, on the otherhand
* `TESTING` is set when the `Set Testing Envrionment` button is clicked in the system tray icon it will only sends to the email addresses specified in the `ME` environment variable.
* `ME` envrionment Variable, list of email addresses used for both testing and as the sender of the email
* `SUB_REDDIT` defines a specific subreddit to use, otherwise it will use random which is simply hitting the api with no specific subreddit in mind.


## Setup

### Packages
Run `pip install -r requirements.txt` to install necessary packages if you'd like to make changes

### Envrionment Variables
* SEND_TO_LIST="\<LIST OF EMAILS\>"
TESTING="\<BOOLEAN SPECIFING WHETHER IN TEST MODE OR NOT\>" OPTIONS: True, False as strings
ME="\<SENDER OF THE EMAIL\>" NOTE: Defaults to Meme-Bot@memes.com if no `ME` envvar is specified
TESTING_SENT_TO_LIST="\<LIST OF TESTING EMAIL\>" NOTE: Used only when TESTING envvar is True
MAILING_SERVER="\<SMTP MAILING SERVER\>"
SUB_REDDIT="ProgrammerHumor" NOTE: Specific Sub reddit to summon memes from.

### Building System Tray Icon

Once you've setup everything, you can run `python setup.py build` and it should build an executable file in a directory called build: `build\exe.win-amd64-3.11\SysTrayIcon.exe`
