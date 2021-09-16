
# tasks
s1_task = SentinelHubInputTask(
    data_collection=DataCollection.SENTINEL1_IW_DES,
    resolution=(120, 120),
    bands_feature=(FeatureType.DATA, 'IW_VV'),
    additional_data=(FeatureType.MASK, 'dataMask', 'IS_DATA'),
    bands=['VV'],
    time_difference=dt.timedelta(minutes=5)
)

reactiv_task = ReactivTask(
    data_feature=(FeatureType.DATA, 'IW_VV'),
    mask_feature=(FeatureType.MASK, 'IS_DATA'),
    reactiv_feature=(FeatureType.DATA_TIMELESS, 'speckle_variability')
)

# workflow
workflow = LinearWorkflow(s1_task, reactiv_task)

result = workflow.execute({
    s1_task: {'bbox': bbox, 'time_interval': time_interval}
})

image = result.eopatch()[(FeatureType.DATA_TIMELESS, 'speckle_variability')]
plot_results(image)