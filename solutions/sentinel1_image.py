# load sample eopatch
eopatch = EOPatch.load('../data/sentinel1_sample/', lazy_loading=True)

# create task using data from sample eopatch
reactiv = ReactivTask((FeatureType.DATA_TIMELESS, 'specle_variability'),
                      data_feature=(FeatureType.DATA, 'IW_VV'),
                      mask_feature=(FeatureType.MASK, 'IS_DATA'))

# run the task
eopatch = reactiv.execute(eopatch)

# plot the results
from skimage import color
plt.figure(figsize=(15,15))
plt.imshow(color.hsv2rgb(eopatch[(FeatureType.DATA_TIMELESS, 'specle_variability')]))