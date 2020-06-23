import configparser
import base64


class EsProperties:
    hostname: str
    port: int
    scheme: str
    username: str
    password: str
    url: str
    number_of_days_to_sample: int

    def __init__(
        self, hostname, port, scheme, username, password, number_of_days_to_sample
    ):
        self.hostname = hostname
        self.port = port
        self.scheme = scheme
        self.username = username
        self.password = password
        self.number_of_days_to_sample = number_of_days_to_sample
        self.url = scheme + "://" + hostname + ":" + port

    def __str__(self):
        return "EsProperties(hostname:{}, port:{}, scheme: {}, username: {}, password: {}, number_of_days_to_sample: {},  url: {})".format(
            self.hostname,
            self.port,
            self.scheme,
            self.username,
            base64.b64encode(self.password.encode("ascii")),
            self.number_of_days_to_sample,
            self.url,
        )

    @staticmethod
    def read_es_properties():
        config = configparser.RawConfigParser()
        config.read("template.ini")
        properties = dict(config.items("ELASTICSEARCH_PROPERTIES"))
        es_properties = EsProperties(
            properties["hostname"],
            properties["port"],
            properties["scheme"],
            properties["username"],
            properties["password"],
            int(properties["number_of_days_to_sample"]),
        )
        return es_properties

