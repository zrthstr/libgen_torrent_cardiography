class Tracker:
    def __init__(self, db):
        self.name = "" # url???
        self.db = db

        # if exists, load
        # else populate with null/none
        self.chk_success_count
        self.chk_fail_count
        self.chk_fail_last
        self.chk_success_last


class Tracker_collection:
    def __init__(self, db):
        #mself.tracker = []
        self.db = db

    def add(self, tracker):
        self.tracker.append(tracker)

    def all(self):
        return [t["name"] for t in self.db.tracker.find()]

    def count(self):
        return db["tracker"].count()

