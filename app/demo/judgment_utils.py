import re
from judgment import Judgment
from logger import Logger


class JudgmentUtils:
    def __init__(self):
        raise NotImplementedError()

    @classmethod
    def __queries_from_header(cls, lines) -> dict:
        """ ファイルのヘッダー行からqid,keywordを抽出 """

        # http://www.regexpal.com/?fam=96564
        regex = re.compile('#\sqid:(\d+?):\s+?(.*)')
        rVal = {}
        for line in lines:
            if line[0] != '#':
                break
            m = re.match(regex, line)
            if m:
                rVal[int(m.group(1))] = m.group(2)

        return rVal

    @classmethod
    def __judgments_from_body(cls, lines):
        """ ファイルのボディ行から判定データ(grade,qid,docId)を抽出 """

        # http://www.regexpal.com/?fam=96565
        regex = re.compile('^(\d)\s+qid:(\d+)\s+#\s+(\w+).*')
        for line in lines:
            Logger.logger.info(line)
            m = re.match(regex, line)
            if m:
                Logger.logger.info("%s,%s,%s" %
                                   (m.group(1), m.group(2), m.group(3)))
                yield m.group(1), m.group(2), m.group(3)

    @classmethod
    def judgments_from_file(cls, filename: str) -> Judgment:
        """ ファイルから判定データを抽出 """

        with open(filename) as f:  # for header
            qid_to_keywords = cls.__queries_from_header(f)

        with open(filename) as f:  # for body
            for grade, qid, docId in cls.__judgments_from_body(f):
                yield Judgment(grade=grade, qid=qid, keywords=qid_to_keywords[int(qid)], doc_id=docId)

    @classmethod
    def judgments_by_qid(cls, judgments) -> dict:
        """ qid毎の判定データ群を取得 """

        r_val = {}
        for j in judgments:
            try:
                r_val[j.qid].append(j)
            except KeyError:
                r_val[j.qid] = [j]
        return r_val
