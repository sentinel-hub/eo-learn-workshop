
class ReactivTask(EOTask):

    def __init__(self, data_feature, mask_feature, reactiv_feature):
        self.data_feature = data_feature
        self.mask_feature = mask_feature
        self.reactiv_feature = reactiv_feature

    def execute(self, eopatch):
        eopatch[self.reactiv_feature] = speckle_variability(
            eopatch[self.data_feature],
            eopatch[self.mask_feature],
            eopatch.timestamp
        )
        return eopatch