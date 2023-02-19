import elasticsearch.helpers
import json
from argparse import ArgumentParser
from logger import Logger
from esutils import Esutils, INDEX_DATA_FILE, INDEX_NAME


def reindex(es_client, movie_dict, index) -> None:
    """ Elasticsearchインデックスの再作成を行った後、bulkリクエストでdoc群をインデックス登録する """

    config = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "index": {
                "analysis": {},
            }}}

    es_client.indices.delete(index=index, ignore=[400, 404])
    es_client.indices.create(index=index, settings=config['settings'])

    try:
        elasticsearch.helpers.bulk(es_client, bulk_docs(
            movie_dict=movie_dict, index=index))
    except Exception as e:
        print(type(e))


def bulk_docs(movie_dict, index) -> dict:
    """ Elasticsearchインデックスに登録するdocをbulkリクエストの形式に変換する """

    for movie_id, movie in movie_dict.items():
        if 'release_date' in movie and movie['release_date'] == "":
            del movie['release_date']

        add_cmd = {"_index": index, "_id": movie_id, "_source": movie}
        yield add_cmd

        if 'title' in movie:
            Logger.logger.info("%s added to %s" %
                               (movie['title'].encode('utf-8'), index))


def parse_commandline_options():
    """ コマンドライン引数を処理する """

    parser = ArgumentParser()
    parser.add_argument('--es-host', dest='es_host',
                        default='http://localhost:9200')
    return parser.parse_args()


def main():
    options = parse_commandline_options()

    # Elasticsearchセットアップ
    es_client = Esutils.create_client(host=options.es_host, timeout=30)

    # Elasticsearchインデックス登録
    tmdb_movie_dict = json.loads(open(INDEX_DATA_FILE).read())
    reindex(es_client, movie_dict=tmdb_movie_dict, index=INDEX_NAME)


if __name__ == "__main__":
    main()
