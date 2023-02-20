import json
import requests
from urllib.parse import urljoin
from logger import Logger
from esutils import FEATURE_SET_NAME

logQueryTmpl = {
    "size": 100,
    "query": {
        "bool": {
            "filter": [
                {
                    "terms": {
                        "_id": ["7555"]
                    }
                }
            ],
            "should": [
                {"sltr": {
                    "_name": "logged_featureset",
                    "featureset": "movie_features",
                    "params": {
                        "keywords": "rambo"
                    }
                }}
            ]
        }
    },
    "ext": {
        "ltr_log": {
            "log_specs": {
                "name": "log_entry1",
                "named_query": "logged_featureset",
                "missing_as_zero": True
            }
        }
    }
}


class FeatureEsutils:
    def __init__(self):
        raise NotImplementedError()

    @classmethod
    def __create_es_log_query(cls, doc_ids: list, keywords) -> dict:
        """ ログ抽出のためのElasticsearchクエリを作成する """

        q = logQueryTmpl

        # "_id": ["7555"] の部分をを書き換える
        q['query']['bool']['filter'][0]['terms']['_id'] = doc_ids

        # "keywords": "rambo" の部分をを書き換える
        q['query']['bool']['should'][0]['sltr']['params']['keywords'] = keywords

        # "featureset": "movie_features" の部分をを書き換える
        q['query']['bool']['should'][0]['sltr']['featureset'] = FEATURE_SET_NAME

        return q

    @classmethod
    def search_logs(cls, es_client, es_index: str, doc_ids: list, keywords) -> dict:
        """ ログ抽出のためにElasticsearchに問い合わせを行う """

        log_query = cls.__create_es_log_query(doc_ids, keywords)

        Logger.logger.info("POST")  # GET?
        Logger.logger.info(json.dumps(log_query, indent=2))
        return es_client.search(index=es_index, body=log_query)

    @classmethod
    def init_default_feature_store(cls, es_host: str):
        """ Elasticsearchのdefault feature storeを初期化する """

        path = urljoin(es_host, '_ltr')

        Logger.logger.info("DELETE %s" % path)
        resp = requests.delete(path)
        Logger.logger.info("%s" % resp.status_code)

        Logger.logger.info("PUT %s" % path)
        resp = requests.put(path)
        Logger.logger.info("%s" % resp.status_code)

    @classmethod
    def create_featureset(cls, es_host: str, feature_set_name: str, feature_set: dict):
        """ Elasticsearchにfeaturesetを作成する """

        path = urljoin(es_host, "_ltr/_featureset/%s" % feature_set_name)

        Logger.logger.info("POST %s" % path)
        Logger.logger.info(json.dumps(feature_set, indent=2))
        resp = requests.post(path, data=json.dumps(feature_set), headers={
            'Content-Type': 'application/json'})
        Logger.logger.info("%s" % resp.status_code)
        Logger.logger.info("%s" % resp.text)

    @staticmethod
    def create_featureset_model(es_host: str, feature_set_name: dict, payload: dict):
        """ Elasticsearchにfeaturesetモデルを作成する """

        path = urljoin(
            es_host, "_ltr/_featureset/%s/_createmodel" % feature_set_name)

        Logger.logger.info("POST %s" % path)
        res = requests.post(path, data=json.dumps(payload), headers={
                            'Content-Type': 'application/json'})
        Logger.logger.info(res.status_code)
        if res.status_code >= 300:
            Logger.logger.error(res.text)
