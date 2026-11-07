from collections.abc import Callable


class MessagingService:
    """
    Keeps the messages of the application (shown at the bottom of every page).

    Other parts of the program can ask to be told whenever the messages change:
    they add a function to the list on_messages_changed, and the service calls
    all the functions from that list after every change (an "event").
    """

    def __init__(self):
        self.messages: list[str] = []
        # the functions to be called when the messages change (the "listeners")
        self.on_messages_changed: list[Callable[[list[str]], None]] = []

    def add(self, message: str) -> None:
        self.messages.append(message)
        self._messages_changed()

    def clear(self) -> None:
        self.messages.clear()
        self._messages_changed()

    def get(self) -> list[str]:
        return self.messages

    def _messages_changed(self) -> None:
        for listener in self.on_messages_changed:
            listener(self.messages)
