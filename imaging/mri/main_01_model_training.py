from imaging.mri.class_BrainLearn import BrainLearn

bl = BrainLearn()
bl.path_main = "E:/gd_synthesis"
# Build dataset
bl.dataset_trn_ratio = 0.7
bl.dataset_val_ratio = 0.2
bl.dataset_tst_ratio = 0.1
bl.build_dataset()
bl.set_roi()
# Compose transformation - Edit the class method to amend
bl.compose_transforms_trn()
bl.compose_transforms_val()
bl.compose_transforms_tst()
# Cache data
bl.cache_dataset_trn()
bl.cache_dataset_val()
bl.cache_dataset_tst()
# Build model
bl.max_iteration_trn = 1000
bl.delta_iteration_trn = 100
bl.build_model_unet(num_res_units=4,
                    channels=(64, 128, 256, 512, 1024),
                    strides=(2, 2, 2, 2))

