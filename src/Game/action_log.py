class ActionLog:
    def __init__(self, players):
        self.log = {player.uuid : [] for player in players}

    def add_message(self, uuid, message):
        self.log[uuid] = message

    def get_messages(self, uuid):
        return self.log[uuid]

    def clear(self):
        for uuid in self.log:
            self.log[uuid] = []

    def reset(self):
        self.log = {}