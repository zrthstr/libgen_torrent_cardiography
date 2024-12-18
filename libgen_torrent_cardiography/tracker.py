from datetime import datetime


class Tracker:
    def __init__(self, db, url):
        self.url = url
        self.db = db

        tra = self.db.tracker.find_one(url=self.url)
        if not tra:
            self.chk_success_count = 0
            self.chk_fail_count = 0
            self.chk_fail_last = None
            self.chk_success_last = None

            self._save_to_db()
            tra = self.db.tracker.find_one(url=self.url)

        self.chk_success_count = tra["chk_success_count"]
        self.chk_fail_count = tra["chk_fail_count"]
        self.chk_fail_last = tra["chk_fail_last"]
        self.chk_success_last = tra["chk_success_last"]

    def increment_fail_count(self):
        self.chk_fail_count += 1
        self.chk_fail_last = datetime.utcnow()
        self._save_to_db()

    def increment_success_count(self):
        self.chk_success_count += 1
        self.chk_success_last = datetime.utcnow()
        self._save_to_db()

    def _save_to_db(self):
        tr = dict(
            url=self.url,
            chk_success_count=self.chk_success_count,
            chk_fail_count=self.chk_fail_count,
            chk_fail_last=self.chk_fail_last,
            chk_success_last=self.chk_success_last,
        )

        self.db.tracker.upsert(tr, ["url"])


class Tracker_collection:
    def __init__(self, db):
        self.db = db

    def add(self, tracker):
        self.tracker.append(tracker)

    def all(self):
        return [t["url"] for t in self.db.tracker.find()]

    def count(self):
        return db["tracker"].count()
