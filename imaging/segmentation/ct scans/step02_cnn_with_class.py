from imaging.segmentation.tools.classes_cnn import *

wrm = NNMealworms()
wrm.buil_dataset()
wrm.get_dxdydz()
wrm.compose_transforms_trn()
wrm.compose_transforms_val()
wrm.compose_transforms_tst()
wrm.cache_data()
wrm.build_unet_model()
wrm.train()
