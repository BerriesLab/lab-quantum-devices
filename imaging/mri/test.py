import monai
import torch

# 1. DATA PRE-PROCESSING

# STEP 1.1: skull stripping -> by HD BET in 3D slicer
# Skull stripping is performed on T1, 1T1 and 1/2T1 MR images

# STEP 1.2: image registration -> by SimpleElastix (SimpleITK) in Python.
# Image registration is performed on (T1, 1T1) and (T1, 1/2T1) pairs separately,
# where T1 is the fixed image (pre-contrast), and 1T1 and 1/2T1 are the moving images (post-contrast).

# STEP 1.3: intensity rescaling -> by z-score in Python
# This is done by calculating the intensity mean and standard deviation of the image sample.
# To avoid running out of memory, the algorithm process one image per time (one MR image - 0.5 GB)

# STEP 1.4: image subtraction -> by dataloader/transformation?
# This could be implemented into a transformers, but it would require defining a class. As a first attempt,
# it would be easier to get the difference with numpy.

# 2. DATASET PREPARATION

# The training, validation and testing dataset must consist of contrast images plus their brain masks. The
# latter is necessary to weight the loss-function.

