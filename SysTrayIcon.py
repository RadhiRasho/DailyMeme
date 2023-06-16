import requests
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pystray import Menu, MenuItem as item
import pystray
from PIL import Image
from pystray import Icon
import schedule
import time
import os

load_dotenv(".env")


def get_meme():
    data = requests.get(
        url="https://meme-api.com/gimme/funny",
        headers={"Content-Type": "application/json"},
    ).json()

    return data


def recursive_Meme_Fetcher():
    try:
        data = get_meme()
        return data if data["nsfw"] == False else recursive_Meme_Fetcher()
    except Exception as e:
        print("Failed to fetch meme due to API being down or private repo", e)
        return recursive_Meme_Fetcher()


def SendMeme(testMode: bool = False) -> bool:
    data = recursive_Meme_Fetcher()

    text = """\
      <html>
      <head></head>
      <body>
        <p>
          <p><strong>r/{subreddit} - u/{author}</strong></p>
          <p><strong>Title: {title}</strong></p>

          <img height='280px' width='900px' src='{url}'></img><br/><br/>
        </p>
      </body>
    </html>
    """.format(
        url=data["preview"][3],
        title=data["title"],
        subreddit=data["subreddit"],
        author=data["author"],
    )

    me = os.getenv("ME", "Meme-Bot@memes.com")

    SentToList = os.getenv(
        "SEND_TO_LIST" if testMode == False else "TESTING_SENT_TO_LIST", me
    )

    MailingServer: str = os.getenv("MAILING_SERVER", "localhost")

    msg = MIMEMultipart("Message")
    msg["Subject"] = "Your Daily Meme"
    msg["From"] = me
    msg["To"] = SentToList

    msg.attach(MIMEText(text, "html"))

    try:
        with SMTP(MailingServer) as smtp:
            for sendTo in SentToList.split(","):
                smtp.sendmail(from_addr=me, to_addrs=sendTo, msg=msg.as_string())
            smtp.quit()
        return True
    except Exception as e:
        print("Failed to send email", e)
        SendMeme(testMode=testMode)
        return True


def quit(icon: Icon):
    schedule.clear()
    icon.notify("Daily Meme", "Scheduled memes have been cancelled")
    icon.stop()


def run_meme(icon: Icon):
    testMode = True if os.getenv("TESTING") == "True" else False
    icon.notify("Daily Meme", "Sending meme...")
    SendMeme(testMode=testMode)


def setup(icon: Icon) -> None:
    testMode = True if os.getenv("TESTING") == "True" else False

    # Schedule the main function to run at 8 am on Monday through Friday
    schedule.every().day.at("10:00").do(SendMeme, testMode=testMode)

    print(schedule.jobs)
    icon.notify("Daily Meme", "Scheduled memes have been started")


def setEnv(icon: Icon):
    if not icon.menu.items[0].checked:
        os.environ["TESTING"] = "True"
        icon.notify("Daily Meme", "Test Mode Enabled")
    else:
        os.environ["TESTING"] = "False"
        icon.notify("Daily Meme", "Test Mode Disabled")


image = Image.open("./favicon.ico")
menu = Menu(
    item(
        "Set Testing Environment",
        setEnv,
        checked=lambda item: os.getenv("TESTING") == "True",
    ),
    item("Run Meme Manully", run_meme),
    item("Quit", quit),
)
icon = pystray.Icon("name", image, "Daily Meme", menu)

icon._start_setup(setup=setup)

icon._mark_ready()

icon.run_detached()

while True:
    schedule.run_pending()
    if not schedule.jobs:
        icon.notify("Daily Meme", "No more memes to send")
        icon.stop()
        break
    time.sleep(1)
