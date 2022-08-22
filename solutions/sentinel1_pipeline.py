s1_task = SentinelHubInputTask(
    data_collection=DataCollection.SENTINEL1_IW_DES,
    resolution=(120, 120),
    bands_feature=(FeatureType.DATA, 'IW_VV'),
    additional_data=(FeatureType.MASK, 'dataMask', 'IS_DATA'),
    bands=['VV'],
    time_difference=dt.timedelta(minutes=5)
)
s1_node = EONode(s1_task, inputs=[], name="Get data from SentinelHub")

reactiv_task = ReactivTask(
    data_feature=(FeatureType.DATA, 'IW_VV'),
    mask_feature=(FeatureType.MASK, 'IS_DATA'),
    reactiv_feature=(FeatureType.DATA_TIMELESS, 'speckle_variability')
)
reactiv_node = EONode(reactiv_task, inputs=[s1_node], name="Run REACTIV algorith,")

# an extra (output) node to retain in memory the outputs of the workflow
output_node = EONode(OutputTask("output_eopatch"), inputs=[reactiv_node])

# workflow
workflow = EOWorkflow(workflow_nodes = (s1_node, reactiv_node, output_node))

result = workflow.execute({
    s1_node: {'bbox': bbox, 'time_interval': time_interval}
})

image = result.outputs["output_eopatch"][(FeatureType.DATA_TIMELESS, 'speckle_variability')]
plot_results(image)