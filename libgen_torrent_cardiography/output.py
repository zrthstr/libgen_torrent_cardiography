
import dataset

# TODO
# move to conf
OUT_HTML = "out.html"
OUT_JSON = "out.json"


class Output:

    def __init__(self, db, config):
        self.db = db
        self.config = config

    def generate_json(self):
        pass

    def generate_html(self):
        pass


    def generate(self):
        self.generate_json()
        self.generate_html()

