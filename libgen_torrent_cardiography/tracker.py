class Tracker:
    def __init__(self):
        pass
    @staticmethod
    def all(db):
        return [t["name"] for t in db["tracker"].find()]



