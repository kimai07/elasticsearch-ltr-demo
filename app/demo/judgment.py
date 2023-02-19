class Judgment:
    def __init__(self, grade, qid, keywords, doc_id):
        self.grade = grade
        self.qid = qid
        self.keywords = keywords
        self.docId = doc_id
        self.features = []  # 0th feature is ranklib feature 1

    def __str__(self):
        return "grade:%s qid:%s (%s) docid:%s" % (self.grade, self.qid, self.keywords, self.docId)

    def to_ranklib_format(self):
        """ ranklibフォーマットに変換する """

        features_as_strs = ["%s:%s" % (idx+1, feature)
                            for idx, feature in enumerate(self.features)]
        comment = "# %s\t%s" % (self.docId, self.keywords)
        return "%s\tqid:%s\t%s %s" % (self.grade, self.qid, "\t".join(features_as_strs), comment)
