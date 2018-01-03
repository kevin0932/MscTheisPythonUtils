###### some python scripts to process input images for my thesis project


### How to do image cropping for DeMoN's Input!
# find some in https://github.com/lmb-freiburg/demon/issues/15

===============================================================================
The following params are checked from database.db file provided in southbuilding dataset with COLMAP.

Width = 3072 Pixels
Height = 2304 Pixels


focal_length_scaled = 2457.6
imgHalfWidth_scaled = 1536
imgHalfHeight_scaled = 1152

===============================================================================
As in the post by Sam Pepose, H = 2304, W=3072.


Demon assumptions: width 256, height 192, (normalized) focal lengths 0.89115971, 1.18821287.


Then find the crop dimensions H' x W' from the relationship between focal length and image dimensions:
(0.89115971)(256) = (fx)(W')
(1.18821287)(192) = (fy)(H')


* Make sure you normalize your fx, fy values (e.g., fx_norm = fx / W).

	fx_norm = fx / W = 2457.6 / 3072 = 0.8
	fy_norm = fy / H = 2457.6 / 2304 = 1.06666666666666666


Therefore,
	(0.89115971)(256) = (2457.6 / 3072)*(W')		=> W' = (0.89115971×256×3072)÷2457.6 = 285.1711072
	(1.18821287)(192) = (2457.6 / 2304)*(H')		=> H' = (1.18821287×192×2304)÷2457.6 = 213.8783166

Then crop a small image in the center of the original image with the size of H' * W' and then resize the crop to the required 192x256 image.

You can then resize this cropped image to the required 192 x 256 dimensions. The principal point is exactly in the image center (0.5, 0.5). This means you should crop with this point as the center.

===============================================================================
By Benjamin:

The normalized intrinsic parameters we trained DeMoN on are:

K = (0.89115971  0           0.5)
    (0           1.18821287  0.5)
    (0           0           1  )

To adjust the focal length of your image, you scale the image such that the normalized focal lengths for the x and y dimension match (0.8911 and 1.1882).

The principal point is exactly in the image center (0.5, 0.5). This means you should crop with this point as the center.
