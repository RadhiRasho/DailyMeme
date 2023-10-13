from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep
from dotenv import load_dotenv
from pystray import Icon, Menu, MenuItem as item
from PIL import Image
import requests
import schedule
import os
import pymsgbox

load_dotenv(".env")

class Meme:
    postLink: str
    subreddit: str
    title: str
    url: str
    nsfw: bool
    spoiler: bool
    author: str
    ups: int
    preview: list[str]

    def __init__(
        self,
        postLink: str,
        subreddit: str,
        title: str,
        url: str,
        nsfw: bool,
        spoiler: bool,
        author: str,
        ups: int,
        preview: list[str],
    ):
        self.postLink = postLink
        self.subreddit = subreddit
        self.title = title
        self.url = url
        self.nsfw = nsfw
        self.spoiler = spoiler
        self.author = author
        self.ups = ups
        self.preview = preview


def get_meme() -> Meme:
    subReddit = os.getenv("SUB_REDDIT", "")
    data = requests.get(
        url=f"https://meme-api.com/gimme/{subReddit}",
        headers={"Content-Type": "application/json"},
    ).json()

    return Meme(**data)


def recursive_Meme_Fetcher() -> Meme:
    try:
        data: Meme = get_meme()
        return data if data.nsfw == False and data.ups > 4000 else recursive_Meme_Fetcher()
    except Exception as ex:
        print("Failed to fetch meme due to API being down or private sub reddit", ex)
        return recursive_Meme_Fetcher()


def SendMeme(testMode: bool = False) -> bool:
    data: Meme = recursive_Meme_Fetcher()

    HTML = """\
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>

        <body>
            <div>
                <div>
                    <span>Author: u/{author}</span>
                    <span>Subreddit: r/{subreddit}</span>
                    <span>Up Votes: {ups}</span>
                </div>
                <h3>Title: {title}</h3>
                <img width="450" alt='meme' src="{url}">
            </div>
        </body>

        </html>
    """

    text = HTML.format(
        url=data.url,
        ups=data.ups,
        title=data.title,
        subreddit=data.subreddit,
        author=data.author,
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
    icon.notify("Daily Meme", "Sending Meme Manually...")
    SendMeme(testMode=testMode)


def setup_icon(icon: Icon):
    testMode = True if os.getenv("TESTING") == "True" else False

    scheduledTime = os.getenv("SCHEDULE_TIME", "10:00")

    schedule.every().day.at(time_str=scheduledTime).do(SendMeme, testMode=testMode)

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
    sendToList = ("TESTING_SENT_TO_LIST" if os.getenv("TESTING") == "True" else "SEND_TO_LIST")
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

def updateCurrentlyScheduledJobs(icon: Icon):
    scheduledTime = os.getenv("SCHEDULE_TIME", "10:00")

    testMode = True if os.getenv("TESTING") == "True" else False
    schedule.clear()
    schedule.every().day.at(time_str=scheduledTime).do(SendMeme, testMode=testMode)

def on_input_text(icon: Icon):
    text = pymsgbox.prompt(title="Daily Meme", text="Enter Time (HH:MM)", default="10:00")
    if text is not None:
        if (len(text.split(":")) != 2) or (len(text.split(":")[0]) != 2) or (len(text.split(":")[1]) != 2):
            icon.notify("Daily Meme", "Invalid Time Format")
        else:
            os.environ.update([("SCHEDULE_TIME", text)])

        icon.notify("Daily Meme", f"Schedule Time Updated to {text}")

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
                checked=lambda item: os.getenv("SUB_REDDIT") == "HistoryMemes",
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
    item("Set Schedule Time", on_input_text),
    item("Update Currently Scheduled Jobs", updateCurrentlyScheduledJobs),
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
    if not icon._running:
        break

exit(0);