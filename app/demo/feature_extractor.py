import json
from logger import Logger
from feature_esutils import FeatureEsutils
from esutils import FEATURE_TMPL_PATH


class FeatureExtractor:
    def __init__(self):
        pass

    def __each_feature(self):
        """ 各特徴量抽出用のクエリをロード """

        try:
            ftr_id = 1
            while True:
                parsed_json = json.loads(
                    open(FEATURE_TMPL_PATH + 'query%s.json' % ftr_id).read())
                template = parsed_json['query']
                feature_spec = {
                    "name": "%s" % ftr_id,
                    "params": ["keywords"],
                    "template": template
                }
                yield feature_spec
                ftr_id += 1
        except IOError:
            pass

    def prepare(self, es_host: str, feature_set_name: str):
        """ 全ての特徴量抽出用のクエリをロード """

        feature_set = {
            "featureset": {
                "name": feature_set_name,
                "features": [feature for feature in self.__each_feature()]
            }
        }
        FeatureEsutils.create_featureset(
            es_host, feature_set_name, feature_set)

    def __feature_dict_to_list(self, ranklib_labeled_features) -> list[float]:
        """ 辞書形式の特徴量をリスト形式に変換する """

        r_val = [0.0] * len(ranklib_labeled_features)
        for idx, logEntry in enumerate(ranklib_labeled_features):
            value = logEntry['value']
            try:
                r_val[idx] = value
            except IndexError:
                Logger.logger.info("Out of range %s" % idx)
        return r_val

    def extract(self, es_client, judgments_dict: dict, es_index: str):
        """ Elasticsearchから取得した各doc毎の特徴量ログをリスト形式に変換してjudgmentに保存する """

        for _, judgments in judgments_dict.items():
            doc_ids = [judgment.docId for judgment in judgments]
            keywords = judgments[0].keywords
            resp = FeatureEsutils.search_logs(es_client, es_index=es_index,
                                              doc_ids=doc_ids, keywords=keywords)

            # Add feature back to each judgment
            features_per_doc = {}
            for doc in resp['hits']['hits']:
                docId = doc['_id']
                features = doc['fields']['_ltrlog'][0]['log_entry1']
                features_per_doc[docId] = self.__feature_dict_to_list(features)

            # Append features from ES back to ranklib judgment list
            for judgment in judgments:
                try:
                    # If KeyError, then we have a judgment but no movie in index
                    features = features_per_doc[judgment.docId]
                    judgment.features = features
                except KeyError:
                    Logger.logger.info("Missing movie %s" % judgment.docId)

    def build_features_judgments_file(self, judgments_with_features: dict, judgment_fname: str):
        """ 特徴量の正解データを書き出す """

        with open(judgment_fname, 'w') as fw:
            for _, judgmentList in judgments_with_features.items():
                for judgment in judgmentList:
                    fw.write(judgment.to_ranklib_format() + "\n")
