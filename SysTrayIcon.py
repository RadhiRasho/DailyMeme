from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pystray import Icon, Menu, MenuItem as item
from PIL import Image
import requests
import schedule
import time
import os
import threading

load_dotenv(".env")


def get_meme():
    subReddit = os.getenv("SUB_REDDIT", "")
    data = requests.get(
        url=f"https://meme-api.com/gimme/{subReddit}",
        headers={"Content-Type": "application/json"},
    ).json()

    return data


def recursive_Meme_Fetcher():
    try:
        data = get_meme()
        return data if data["nsfw"] == False else recursive_Meme_Fetcher()
    except Exception as e:
        print("Failed to fetch meme due to API being down or private sub reddit", e)
        return recursive_Meme_Fetcher()


def SendMeme(testMode: bool = False) -> bool:
    data = recursive_Meme_Fetcher()

    text = """\
      <html>
      <head></head>
      <body>
        <p>
          <h3> r/{subreddit} - u/{author} </h3>
          <h3>Title: {title} </h3>

          <img height='280px' width='900px' src='{url}'></img><br/><br/>
        </p>
      </body>
    </html>
    """.format(
        url=data["url"],
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
        smtp.close()
    except Exception as e:
        print("Failed to send email", e)
        SendMeme(testMode=testMode)
    finally:
        return True


def quit(icon: Icon):
    schedule.clear()
    icon.notify("Daily Meme", "Scheduled memes have been cancelled")
    icon.stop()


def run_meme(icon: Icon):
    testMode = True if os.getenv("TESTING") == "True" else False
    icon.notify("Daily Meme", "Sending meme...")
    SendMeme(testMode=testMode)


def setup_icon(icon: Icon):
    def setup_scheduler():
        testMode = True if os.getenv("TESTING") == "True" else False
        schedule.every().day.at("10:00").do(SendMeme, testMode=testMode)

    _setup_thread = threading.Thread(target=setup_scheduler)
    _setup_thread.start()

    icon.notify("Daily Meme", "Scheduled memes have been started")


def setEnv(icon: Icon, item: item):
    if not item.checked:
        os.environ["TESTING"] = "True"
        icon.notify("Daily Meme", "Test Mode Enabled")
    else:
        os.environ["TESTING"] = "False"
        icon.notify("Daily Meme", "Test Mode Disabled")


def scheduledJobs(icon: Icon):
    icon.notify(f"{schedule.jobs}")


def checkSendToList(icon: Icon):
    sendToList = (
        "TESTING_SENT_TO_LIST" if os.getenv("TESTING") == "True" else "SEND_TO_LIST"
    )

    icon.notify(f"{os.getenv(sendToList)}")


def updatedSubReddit(icon: Icon, item: item):
    match item.text:
        case "r/funny":
            os.environ.update({"SUB_REDDIT": "funny"})
        case "r/memes":
            os.environ.update({"SUB_REDDIT": "memes"})
        case "r/dankmemes":
            os.environ.update({"SUB_REDDIT": "dankmemes"})
        case "r/wholesomememes":
            os.environ.update({"SUB_REDDIT": "wholesomememes"})
        case "r/ProgrammerHumor":
            os.environ.update({"SUB_REDDIT": "ProgrammerHumor"})
        case "r/Animemes":
            os.environ.update({"SUB_REDDIT": "Animemes"})
        case "r/HistoryMemes":
            os.environ.update({"SUB_REDDIT": "HistoryMemes"})
        case _:
            os.environ.update({"SUB_REDDIT": ""})

    icon.notify("Daily Meme", f"Sub-Reddit Updated to {item.text}")


image = Image.open("./favicon.ico")
menu = Menu(
    item(
        "Set Testing Environment",
        setEnv,
        checked=lambda item: os.getenv("TESTING") == "True",
    ),
    item("Run Meme Manully", run_meme),
    item(
        "Set Sub-Reddit",
        Menu(
            item(
                "r/funny",
                updatedSubReddit,
                checked=lambda item: os.getenv("SUB_REDDIT") == "funny",
            ),
            item(
                "r/memes",
                updatedSubReddit,
                checked=lambda item: os.getenv("SUB_REDDIT") == "memes",
            ),
            item(
                "r/dankmemes",
                updatedSubReddit,
                checked=lambda item: os.getenv("SUB_REDDIT") == "dankmemes",
            ),
            item(
                "r/wholesomememes",
                updatedSubReddit,
                checked=lambda item: os.getenv("SUB_REDDIT") == "wholesomememes",
            ),
            item(
                "r/ProgrammerHumor",
                updatedSubReddit,
                checked=lambda item: os.getenv("SUB_REDDIT") == "ProgrammerHumor",
            ),
            item(
                "r/PrequelMemes",
                updatedSubReddit,
                checked=lambda item: os.getenv("SUB_REDDIT") == "PrequelMemes",
            ),
            item(
                "r/Animemes",
                updatedSubReddit,
                checked=lambda item: os.getenv("SUB_REDDIT") == "Animemes",
            ),
            item(
                "r/HistoryMemes",
                updatedSubReddit,
                checked=lambda item: os.getenv("SUB_REDDIT") == "historymemes",
            ),
            item(
                "Random Sub",
                updatedSubReddit,
                checked=lambda item: os.getenv("SUB_REDDIT") == "",
            ),
        ),
    ),
    item("Check Send To List", checkSendToList),
    item("Scheduled Jobs", scheduledJobs),
    item("Quit", quit),
)

iconName = "Daily Meme Test Mode" if os.getenv("TESTING") == "True" else "Daily Meme"

icon = Icon(
    "name",
    image,
    iconName,
    menu,
)

icon._start_setup(setup=setup_icon)

icon._mark_ready()

icon.run_detached()

while True:
    schedule.run_pending()
    if not schedule.jobs:
        icon.notify("Daily Meme", "No more memes to send")
        icon.stop()
        break
    time.sleep(1)
