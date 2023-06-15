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


def get_meme() -> str:
    data = requests.get(
        url="https://meme-api.com/gimme",
        headers={"Content-Type": "application/json"},
    ).json()

    return data["preview"][3]


def recursive_Meme_Fetcher() -> str:
    try:
        return get_meme()
    except Exception as e:
        print("Failed to fetch meme due to API being down or private repo", e)
        return recursive_Meme_Fetcher()


def SendMeme(testMode: bool = False) -> None:
    url: str = recursive_Meme_Fetcher()
    text = """\
      <html>
      <head></head>
      <body>
        <p>
          <p>Friendly Advisory: This email contains a meme.</p><br/>
          <img height='280px' width='900px' src='{url}'></img><br/><br/>
        </p>
      </body>
    </html>
    """.format(
        url=url
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
    except Exception as e:
        print("Failed to send email", e)
        SendMeme(testMode=testMode)


def quit(icon: Icon):
    schedule.clear()
    time.sleep(5)
    icon.stop()


def run_meme(icon: Icon, TestMode: bool):
    icon.notify("Daily Meme", "Sending meme...")
    SendMeme(testMode=TestMode)


def setup(icon: Icon):
    testMode = True if os.getenv("TESTING") == "True" else False

    # Schedule the main function to run at 8 am on Monday through Friday

    schedule.every().day.at("10:00", "America/Chicago").do(SendMeme, testMode=testMode)


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
