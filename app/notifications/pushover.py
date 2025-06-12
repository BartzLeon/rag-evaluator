import os
import logging
import time
import requests
import dotenv

BASE_URL = "https://api.pushover.net/1/"
MESSAGE_URL = BASE_URL + "messages.json"
USER_URL = BASE_URL + "users/validate.json"
SOUND_URL = BASE_URL + "sounds.json"
RECEIPT_URL = BASE_URL + "receipts/"
GLANCE_URL = BASE_URL + "glances.json"


class RequestError(Exception):
    """Exception which is raised when Pushover's API returns an error code.

    The list of errors is stored in the :attr:`errors` attribute.
    """

    def __init__(self, errors):
        super().__init__()
        self.errors = errors

    def __str__(self):
        return "\n==> " + "\n==> ".join(self.errors)


class Request:
    """Base class to send a request to the Pushover server and check the return
    status code. The request is sent on instantiation and raises
    a :class:`RequestError` exception when the request is rejected.
    """

    def __init__(self, method, url, payload):
        files = {}
        if "attachment" in payload:
            files["attachment"] = payload["attachment"]
            del payload["attachment"]
        self.payload = payload
        self.files = files
        request = getattr(requests, method)(url, params=payload, files=files)
        self.answer = request.json()
        if 400 <= request.status_code < 500:
            raise RequestError(self.answer["errors"])

    def __str__(self):
        return str(self.answer)


class MessageRequest(Request):
    """This class represents a message request to the Pushover API. You do not
    need to create it yourself, but the :func:`Pushover.message` function
    returns :class:`MessageRequest` objects.

    The :attr:`answer` attribute contains a JSON representation of the answer
    made by the Pushover API. When sending a message with a priority of 2, you
    can poll the status of the notification with the :func:`poll` function.
    """

    params = {
        "expired": "expires_at",
        "called_back": "called_back_at",
        "acknowledged": "acknowledged_at",
    }

    def __init__(self, payload):
        super().__init__("post", MESSAGE_URL, payload)
        self.status = {"done": True}
        if payload.get("priority", 0) == 2:
            self.url = RECEIPT_URL + self.answer["receipt"]
            self.status["done"] = False
            for param, when in self.params.items():
                self.status[param] = False
                self.status[when] = 0

    def poll(self):
        """If the message request has a priority of 2, Pushover keeps sending
        the same notification until the client acknowledges it. Calling the
        :func:`poll` function fetches the status of the :class:`MessageRequest`
        object until the notifications either expires, is acknowledged by the
        client, or the callback url is reached. The status is available in the
        ``status`` dictionary.

        Returns ``True`` when the request has expired or been acknowledged and
        ``False`` otherwise so that a typical handling of a priority-2
        notification can look like this::

            request = p.message("Urgent!", priority=2, expire=120, retry=60)
            while not request.poll():
                # do something
                time.sleep(5)

            print(request.status)
        """
        if not self.status["done"]:
            r = Request("get", self.url + ".json", {"token": self.payload["token"]})
            for param, when in self.params.items():
                self.status[param] = bool(r.answer[param])
                self.status[when] = int(r.answer[when])
            for param in ["acknowledged_by", "acknowledged_by_device"]:
                self.status[param] = r.answer[param]
            self.status["last_delivered_at"] = int(r.answer["last_delivered_at"])
            if any(self.status[param] for param in self.params):
                self.status["done"] = True
        return self.status["done"]

    def cancel(self):
        """If the message request has a priority of 2, Pushover keeps sending
        the same notification until it either reaches its ``expire`` value or
        is aknowledged by the client. Calling the :func:`cancel` function
        cancels the notification early.
        """
        if not self.status["done"]:
            return Request(
                "post", self.url + "/cancel.json", {"token": self.payload["token"]}
            )
        else:
            return None


class Pushover:
    """This is the main class of the module. It represents a Pushover app and
    is tied to a unique API token.

    * ``token``: Pushover API token
    """

    _SOUNDS = None
    message_keywords = [
        "title",
        "priority",
        "sound",
        "callback",
        "timestamp",
        "url",
        "url_title",
        "device",
        "retry",
        "expire",
        "html",
        "attachment",
    ]
    glance_keywords = ["title", "text", "subtext", "count", "percent", "device"]

    def __init__(self, token):
        self.token = token

    @property
    def sounds(self):
        """Return a dictionary of sounds recognized by Pushover and that can be
        used in a notification message.
        """
        if not self._SOUNDS:
            request = Request("get", SOUND_URL, {"token": self.token})
            self._SOUNDS = request.answer["sounds"]
        return self._SOUNDS

    def verify(self, user, device=None):
        """Verify that the `user` and optional `device` exist. Returns
        `None` when the user/device does not exist or a list of the user's
        devices otherwise.
        """
        payload = {"user": user, "token": self.token}
        if device:
            payload["device"] = device
        try:
            Request("post", USER_URL, payload)
        except RequestError:
            return None
        else:
            return

    def message(self, user, message, **kwargs):
        """Send `message` to the user specified by `user`. It is possible
        to specify additional properties of the message by passing keyword
        arguments. The list of valid keywords is ``title, priority, sound,
        callback, timestamp, url, url_title, device, retry, expire and html``
        which are described in the Pushover API documentation.

        For convenience, you can simply set ``timestamp=True`` to set the
        timestamp to the current timestamp.

        An image can be attached to a message by passing a file-like object
        to the `attachment` keyword argument.

        This method returns a :class:`MessageRequest` object.
        """

        payload = {"message": message, "user": user, "token": self.token}
        for key, value in kwargs.items():
            if key not in self.message_keywords:
                raise ValueError("{0}: invalid message parameter".format(key))
            elif key == "timestamp" and value is True:
                payload[key] = int(time.time())
            elif key == "sound" and value not in self.sounds:
                raise ValueError("{0}: invalid sound".format(value))
            else:
                payload[key] = value

        return MessageRequest(payload)

    def glance(self, user, **kwargs):
        """Send a glance to the user. The default property is ``text``, as this
        is used on most glances, however a valid glance does not need to
        require text and can be constructed using any combination of valid
        keyword properties. The list of valid keywords is ``title, text,
        subtext, count, percent and device`` which are  described in the
        Pushover Glance API documentation.

        This method returns a :class:`Request` object.
        """
        payload = {"user": user, "token": self.token}

        for key, value in kwargs.items():
            if key not in self.glance_keywords:
                raise ValueError("{0}: invalid glance parameter".format(key))
            else:
                payload[key] = value

        return Request("post", GLANCE_URL, payload)

logger = logging.getLogger(__name__)

class PushoverNotifier:
    def __init__(self):
        # Load .env first
        dotenv.load_dotenv()

        # Then load .env.local which will override any values from .env
        dotenv.load_dotenv(".env.local", override=True)
        self.user_key = os.getenv("PUSHOVER_USER_KEY")
        api_token = os.getenv("PUSHOVER_API_TOKEN")

        if not self.user_key or not api_token:
            logger.warning("Pushover credentials not set. Notifications will be disabled.")
            self.client = None
        else:
            logger.info(f"Pushover credentials loaded: {self.user_key} and {api_token}")
            self.client = Pushover(api_token)

    def send_message(self, message: str, title: str) -> None:
        if self.client and self.user_key:
            try:
                client = self.client.message(self.user_key, message, title=title)
                logger.info(f"Pushover notification sent: {title}")
                logger.info(f"Pushover notification response: {client}")
            except RequestError as e:
                logger.error(f"Failed to send Pushover notification due to request error: {e.errors}")
            except Exception as e:
                logger.error(f"Failed to send Pushover notification: {e}") 