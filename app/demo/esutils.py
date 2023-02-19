import configparser
import elasticsearch

config = configparser.ConfigParser()
config.read('settings.cfg')

RANKLIB_JAR = config['DEFAULT']['RanklibJar']
FEATURE_TMPL_PATH = config['DEFAULT']['FeatureTmplPath']
FEATURE_SET_NAME = config['DEFAULT']['FeatureSetName']
JUDGMENTS_FILE = config['DEFAULT']['JudgmentsFile']
JUDGMENTS_FILE_FEATURES = config['DEFAULT']['JudgmentsFileWithFeature']
INDEX_DATA_FILE = config['DEFAULT']['IndexDataFile']
INDEX_NAME = config['DEFAULT']['IndexName']


class Esutils:
    @classmethod
    def create_client(cls, host=None, timeout=1000) -> elasticsearch.Elasticsearch:
        """ low-level Elasticsearchクライアントを作成する """
        return elasticsearch.Elasticsearch(host, timeout=timeout)
