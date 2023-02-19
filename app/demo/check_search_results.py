from argparse import ArgumentParser
from esutils import Esutils


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
    if model_type in model_type_map:
        return True
    return False


def get_model_type_map(model_type: int) -> str:
    if model_type in model_type_map:
        return model_type_map[model_type]
    return ""


def create_es_query(keyword: str) -> dict:
    """ LTR無しのElasticsearchクエリを作成する """

    query = {
        "query": {
            "multi_match": {
                "query": keyword,
                "fields": ["title", "overview"]
            }
        }
    }
    return query


def create_es_ltr_query(keyword: str, model_name: str = "test_6") -> dict:
    """ LTR有りのElasticsearchクエリを作成する """

    query = create_es_query(keyword)
    rescore = {
        "query": {
            "rescore_query": {
                "sltr": {
                    "params": {
                        "keywords": keyword
                    },
                    "model": model_name
                }
            }
        }
    }

    query["rescore"] = rescore
    return query


def show_es_results(res: dict):
    """ Elasticsearchレスポンスの各映画(hits)からタイトル(_sourceのtitle)を出力する """

    hits = res.get('hits').get('hits')
    for i, hit in enumerate(hits):
        print("{} {} ({}, {})".format(i+1, hit['_source']
              ['title'], hit['_source']['id'], hit['_score']))
    print('')


def parse_commandline_options():
    """ コマンドライン引数を処理する """

    parser = ArgumentParser()
    parser.add_argument('--es-host', dest='es_host',
                        default='http://localhost:9200')
    parser.add_argument('--es-index', dest='es_index', default='tmdb')
    parser.add_argument('--keyword', dest='keyword', default='Rambo')
    parser.add_argument('--model-type', dest='model_type', type=int, default=6)
    return parser.parse_args()


def main():
    options = parse_commandline_options()
    search_keyword = options.keyword
    model_type = options.model_type
    if validate_model_type(model_type) == False:
        print("[ERROR] model_type [%s] is invalid." % model_type)
        exit(1)
    model_name = "test_%d" % model_type

    # Elasticsearchセットアップ
    es_host = options.es_host
    es_index = options.es_index
    es_client = Esutils.create_client(host=es_host)

    # Elasticsearchリクエスト結果比較
    print('## search with learning-to-rank (%s is %s model)' %
          (model_name, get_model_type_map(model_type)))
    es_query = create_es_ltr_query(
        keyword=search_keyword, model_name=model_name)
    res = es_client.search(
        index=es_index, query=es_query['query'], rescore=es_query['rescore'], request_timeout=60)
    show_es_results(res)

    print('## search without learning-to-rank')
    es_query = create_es_query(search_keyword)
    res = es_client.search(
        index=es_index, query=es_query['query'], request_timeout=60)
    show_es_results(res)


if __name__ == '__main__':
    main()
