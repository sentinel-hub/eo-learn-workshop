
# tasks
s1_task = S1IWWCSInput('IW_VV', resx='120m', resy='120m',
                       orbit='descending', time_difference=dt.timedelta(minutes=5))

reactiv = ReactivTask((FeatureType.DATA_TIMELESS, 'specle_variability'),
                      data_feature=(FeatureType.DATA, 'IW_VV'),
                      mask_feature=(FeatureType.MASK, 'IS_DATA'))

# workflow
workflow = LinearWorkflow(s1_task, reactiv)

result = workflow.execute({
    s1_task: {'bbox': bbox, 'time_interval': time_interval}
})

plot_results(result.eopatch()[(FeatureType.DATA_TIMELESS, 'specle_variability')])