
class ReactivTask(EOTask):

    def __init__(self,
                 reactiv_feature=(FeatureType.DATA_TIMELESS, 'specle_variability'),
                 data_feature=(FeatureType.DATA, 'IW_VV'),
                 mask_feature=(FeatureType.MASK, 'IS_DATA')):
        self.reactiv_feature = reactiv_feature
        self.data_feature = data_feature
        self.mask_feature = mask_feature

    def execute(self, eopatch):
        eopatch[self.reactiv_feature] = specle_variability(
            eopatch[self.data_feature],
            eopatch[self.mask_feature],
            eopatch.timestamp
        )
        return eopatch