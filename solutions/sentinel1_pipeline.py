# parameters
bbox = BBox(bbox=[-5.996475, 35.706378, -5.285797, 36.157836], crs=CRS.WGS84).transform(CRS.UTM_30N)
time_interval=('2018-01-01','2018-12-31')

# tasks
s1_task = S1IWWCSInput('IW_VV', resx='120m', resy='120m', orbit='descending', time_difference=datetime.timedelta(minutes=5))
reactiv = ReactivTask((FeatureType.DATA_TIMELESS, 'specle_variability'),
                      data_feature=(FeatureType.DATA, 'IW_VV'),
                      mask_feature=(FeatureType.MASK, 'IS_DATA'))

# workflow
from eolearn.core import LinearWorkflow
workflow = LinearWorkflow(s1_task, reactiv)

result = workflow.execute({
    s1_task: {'bbox': bbox, 'time_interval': time_interval},
    reactiv: {}
})

from skimage import color
plt.figure(figsize=(15,15))
plt.imshow(color.hsv2rgb(result.eopatch()[(FeatureType.DATA_TIMELESS, 'specle_variability')]))