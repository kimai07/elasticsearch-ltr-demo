import os
import time
from argparse import ArgumentParser
from time import sleep
from logger import Logger
from feature_extractor import FeatureExtractor
from feature_esutils import FeatureEsutils
from judgment_utils import JudgmentUtils
from esutils import Esutils, RANKLIB_JAR, FEATURE_SET_NAME, JUDGMENTS_FILE, JUDGMENTS_FILE_FEATURES, INDEX_NAME


def train_model(judgments_with_features_file: str, model_output: str, which_model=6):
    """ ranklibモデル学習を行う """

    cmd = "java -jar %s -ranker %s -train %s -save %s -frate 1.0" % \
          (RANKLIB_JAR, which_model, judgments_with_features_file, model_output)
    Logger.logger.info(
        "*********************************************************************")
    Logger.logger.info(
        "*********************************************************************")
    Logger.logger.info("Running %s" % cmd)
    os.system(cmd)


def save_model(es_host, script_name: str, feature_set_name: str, model_fname: str):
    """ Elasticsearchにranklibモデルを保存する """

    model_payload = {
        "model": {
            "name": script_name,
            "model": {
                "type": "model/ranklib",
                "definition": {
                }
            }
        }
    }

    with open(model_fname) as f:
        model_content = f.read()
        model_payload['model']['model']['definition'] = model_content
        FeatureEsutils.create_featureset_model(
            es_host, feature_set_name, model_payload)


model_type_map = {
    0: "MART",  # gradient boosted regression tree
    1: "RankNet",
    2: "RankBoost",
    3: "AdaRank",
    4: "Coordinate Ascent",
    5: "LambdaRank",
    6: "LambdaMART",
    7: "ListNET",
    8: "Random Forests",
    9: "Linear Regression",
}


def validate_model_type(model_type: int) -> bool:
    if model_type is None or model_type in model_type_map:
        return True
    return False


def parse_commandline_options():
    """ コマンドライン引数を処理する """

    parser = ArgumentParser()
    parser.add_argument('--es-host', dest='es_host',
                        default='http://localhost:9200')
    parser.add_argument('--model-type', dest='model_type', type=int)
    return parser.parse_args()


def main():
    options = parse_commandline_options()
    es_host = options.es_host
    es_client = Esutils.create_client(host=es_host, timeout=1000)

    if validate_model_type(options.model_type) == False:
        print("[ERROR] model_type [%s] is invalid." % model_type)
        exit(1)

    # default_feature_storeセットアップ
    FeatureEsutils.init_default_feature_store(es_host=es_host)

    # 特徴量セット定義
    fe = FeatureExtractor()
    fe.prepare(es_host=es_host, feature_set_name=FEATURE_SET_NAME)

    # 判定データの読み込み
    movie_judgments = JudgmentUtils.judgments_by_qid(
        JudgmentUtils.judgments_from_file(JUDGMENTS_FILE))

    # 判定データの特徴量抽出
    fe.extract(es_client=es_client, judgments_dict=movie_judgments,
               es_index=INDEX_NAME)

    # 特徴量付きの判定データのファイル書き出し
    fe.build_features_judgments_file(movie_judgments, JUDGMENTS_FILE_FEATURES)

    model_file = './data/model/model.txt'
    for model_type in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
        if options.model_type is not None and options.model_type != model_type:
            continue

        Logger.logger.info("*** Training %d start." % model_type)
        # モデル学習
        train_model(judgments_with_features_file=JUDGMENTS_FILE_FEATURES,
                    model_output=model_file, which_model=model_type)
        # 学習モデルをElasticsearchにアップロード
        save_model(es_host, script_name="test_%d" % model_type,
                   feature_set_name=FEATURE_SET_NAME, model_fname=model_file)
        Logger.logger.info("*** Training %d end. ***\n\n" % model_type)

        time.sleep(3)


if __name__ == "__main__":
    main()
