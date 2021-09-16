
# load a sample eopatch
eopatch = EOPatch.load('../data/sentinel1_sample')

# create a task using data from the eopatch
reactiv_task = ReactivTask(
    data_feature=(FeatureType.DATA, 'IW_VV'),
    mask_feature=(FeatureType.MASK, 'IS_DATA'),
    reactiv_feature=(FeatureType.DATA_TIMELESS, 'speckle_variability')
)

# run the task
eopatch = reactiv_task.execute(eopatch)

# plot the results
image = eopatch[(FeatureType.DATA_TIMELESS, 'speckle_variability')]
plot_results(image)