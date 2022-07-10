import cv2
import numpy as np
import keyboard
import template_finder
from logger import Logger
from config import Config
from utils.misc import wait
from screen import convert_abs_to_screen, grab

def find_cross_on_map(img: np.array, name: str, roi, YCbCr = False) -> tuple[float, float]:
    center_area = img[roi[1]:roi[1]+roi[3],roi[0]:roi[0]+roi[2]]
    color_range = Config().colors[name+"_cross"]
    if YCbCr:
        converted = cv2.cvtColor(center_area, cv2.COLOR_BGR2YCrCb)
    else:
        converted = cv2.cvtColor(center_area, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(converted, color_range[0], color_range[1])
    if cv2.countNonZero(mask) < 10:
        return None
    dist = cv2.distanceTransform(~mask, cv2.DIST_L1, cv2.DIST_MASK_3)
    k = 5
    bw = np.uint8(dist < k)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    bw2 = cv2.morphologyEx(bw, cv2.MORPH_ERODE, kernel)
    contours, _ = cv2.findContours(bw2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    largest_contour = -1
    for i,c in enumerate(contours):
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
            largest_contour = i
    m = cv2.moments(contours[largest_contour])
    center = (m['m10']/m['m00']+roi[0]-0.5, m['m01']/m['m00']+roi[1]-5)
    print(center)
    return center

def toggle_automap(active: bool = None) -> bool:
    """
    Helper function that will check if the Automap is active (and optionally activate or deactivate it)
    :param active: "True" - activated, "False" - deactivated, "None" - toggle without check. default "None"
    :returns a TemplateMatch object
    """
    if active is None:
        keyboard.send(Config().char["show_automap"])
    elif active:
        if template_finder.search(["MAP_CHECK"], inp_img=grab(force_new=True), roi=[1100,10,160,40], threshold=0.9).valid: #check if the Automap is already on
            Logger.debug("Automap Status: "+ '\033[92m' + "ALREADY ON" + '\033[0m')
        else:
            keyboard.send(Config().char["show_automap"])
            #we should put a keybinding for switching show_items OFF!
            wait(0.1,0.15)
    else:
        keyboard.send(Config().char["clear_screen"])
        wait(0.1,0.15)
    return True


def map_capture(active: bool = True) -> bool:
    """Gets 3 captures of the map:
        1. Before map displayed
        2. Map displayed (tab pressed)
        3. Map displayed a few frames later (tab still pressed)
    Tab is then depressed. The purpose for the third grab is to filter out any animations, later.
    :returns a the image grabbed "img" and the map "during_1" and without the map "during_2"
    """

    # Map OFF
    pre = np.array(grab())
    pre = cv2.cvtColor(pre, cv2.COLOR_BGRA2BGR)
    keyboard.send(Config().char["show_automap"])
    wait(.075)

    # Map ON
    during_1 = np.array(grab())
    during_1 = cv2.cvtColor(during_1, cv2.COLOR_BGRA2BGR)
    wait(.075)

    # Map ON, but we can tell if any carvers/flames are underneath fucking up the diff
    during_2 = np.array(grab())
    during_2 = cv2.cvtColor(during_2, cv2.COLOR_BGRA2BGR)
    keyboard.send(Config().char["show_automap"])

    return pre, during_1, during_2


def _mask_image(img, color, background="None"):
    range_start, range_end = _color_rgb_to_bgr_range(color)
    img_mask = cv2.inRange(img, range_start, range_end)

    # expand what we found to cover the whole thing, make the whole blur part of the mask via threshold
    img_mask = cv2.blur(img_mask, (4, 4))
    _, img_mask = cv2.threshold(img_mask, int(0.1 * 255), 255, cv2.THRESH_BINARY)

    if background == "None":
        return cv2.bitwise_and(img, img, mask=255 - img_mask)
    else:
        return cv2.bitwise_and(img, img, mask=255 - img_mask)


def _color_rgb_to_bgr_range(color, range=1.0):
    r, g, b = color
    offset = int(range / 2)
    # return (b - offset, g - offset, r - offset), (b + offset, g + offset, r + offset)
    return (b - (12 * range), g - (8 * range), r - (8 * range)), (b + (12 * range), g + (8 * range), r + (8 * range))


def _remove_range(img, range_start, range_end):
    img_mask = cv2.inRange(img, range_start, range_end)

    # Debug showing mask
    #cv2.imshow('mask', img_mask)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    # expand what we found to cover the whole thing, make the whole blur part of the mask via threshold
    img_mask = cv2.blur(img_mask, (4, 4))
    _, img_mask = cv2.threshold(img_mask, int(0.1 * 255), 255, cv2.THRESH_BINARY)
    return cv2.bitwise_and(img, img, mask=255 - img_mask)


def map_diff(pre, during_1, during_2, is_start=False, show_current_location=True, threshold=0.11):
    """Takes the 3 stages of map capture and outputs a final diff, removing carvers and adding our own markers"""

    # image without map
    pre = cv2.cvtColor(pre, cv2.COLOR_BGR2GRAY)

    # images displaying the map, clean up some things from this display so it's less cluttered
    original_during_1 = during_1.copy()

    # during_1 = _mask_image(during_1, (0x20, 0x84, 0xF6))  # player marker
    # during_1 = _mask_image(during_1, (0x44, 0x70, 0x74))  # merc marker
    # during_1 = _mask_image(during_1, (0xff, 0xff, 0xff))  # npc marker

    # TODO: HSV it up..
    #   1. White (i.e. npc) is HSV (0, 1, 75%) through (0, 0, 100)
    #   2. Blue on minimap (i.e. you) is HSV (210, 85%, 85%) through (215, 87%, 99%)
    #   3. Greenish on minimap (i.e. merc) is HSV (180, 40%, 40%) through (190, 42%, 42%)
    during_1 = cv2.cvtColor(during_1, cv2.COLOR_BGR2HSV)
    # during_1 = _remove_range(during_1, (0, 0, .75 * 255), (0, 25, 255))  # white npcs
    # during_1 = _remove_range(during_1, (210, .85 * 255, .85 * 255), (215, .90 * 255, 255))  # blue, current player marker
    # during_1 = _remove_range(during_1, (180, .4 * 255, .4 * 255), (190, .42 * 255, .42 * 255))  # green mercs
    masks_to_remove = [
        cv2.inRange(during_1, (0, 0, .75 * 255), (0, 25, 255)),  # white npcs
        # cv2.inRange(during_1, (200, .80 * 255, .85 * 255), (215, .95 * 255, 255)),  # blue, current player marker
        cv2.inRange(during_1, (105, int(.85 * 255), int(.8 * 255)), (110, int(.90 * 255), int(1 * 255))),  # blue, current player marker
        # (185,41,45) .. (183,37,41) .. (184,40,39)
        cv2.inRange(during_1, (90, int(.35 * 255), int(.35 * 255)), (95, int(.45 * 255), int(.50 * 255))),  # green mercs

        # TODO: Yellow warps ??? Red portal ?? remove it, but re-add it colored as warp?
    ]

    # Debug showing masked things being removed
    # cv2.imshow('mask', during_1)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    during_1 = cv2.cvtColor(during_1, cv2.COLOR_HSV2BGR)  # convert it to bgr which lets us convert to gray..
    during_1 = cv2.cvtColor(during_1, cv2.COLOR_BGR2GRAY)
    # during_2 = cv2.cvtColor(during_2, cv2.COLOR_BGR2GRAY)

    # Get diff of original pre-map image vs both map snapshots, combine the artifacts from both snapshots
    absdiff_1 = cv2.absdiff(pre, during_1)
    # _, thresholded_1 = cv2.threshold(absdiff_1, int(threshold * 255), 255, cv2.THRESH_BINARY)

    # absdiff_2 = cv2.absdiff(pre, during_2)
    # _, thresholded_2 = cv2.threshold(absdiff_2, int(threshold * 255), 255, cv2.THRESH_BINARY)

    # diffed = cv2.bitwise_and(thresholded_1, thresholded_2)
    # diffed = thresholded_1
    diffed = absdiff_1

    # earlier we masked some things from the minimap, remove them now post-diff
    for mask_locations in masks_to_remove:
        img_mask = cv2.blur(mask_locations, (2, 2))
        _, img_mask = cv2.threshold(img_mask, int(0.1 * 255), 255, cv2.THRESH_BINARY)

        diffed = cv2.bitwise_and(diffed, diffed, mask=255 - img_mask)

    # Debug showing diff before adding circles
    # cv2.imshow('absdiff_1', absdiff_1)
    # cv2.waitKey(0)
    # cv2.imshow('absdiff_2', absdiff_2)
    # cv2.waitKey(0)
    # cv2.imshow('diffed', diffed)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Draw a big red/green circle + warps that will stick around between images
    diffed = cv2.cvtColor(diffed, cv2.COLOR_GRAY2BGR)

    # TODO: RE-DO WARP MASKS WITH HSV!

    # # were there any warps here? highlight them!
    # # range_start, range_end = color_rgb_to_bgr_range((0xD9, 0x58, 0xEB))  # gets top of warp
    # # range_start, range_end = color_rgb_to_bgr_range((0xA2, 0x46, 0xEA))  # middle of warp
    # # range_start, range_end = color_rgb_to_bgr_range((0xB5, 0x4C, 0xEB))  # middle of warp
    # range_start, range_end = _color_rgb_to_bgr_range((0x8D, 0x3C, 0xB2), range=1.5)  # middle of warp
    # # range_start, range_end = (0xEB - 15, 0x58 - 15, 0xD9 - 15), (0xEA + 15, 0x46 + 15, 0xA2 + 15)
    # warp_mask = cv2.inRange(original_during_1, range_start, range_end)
    # warp_mask = cv2.blur(warp_mask, (5, 5))
    # _, warp_mask = cv2.threshold(warp_mask, int(0.1 * 255), 255, cv2.THRESH_BINARY)
    #
    # diffed[warp_mask > 0] = [0xD9, 0x58, 0xEB]  # Where ever there is a warp color it in with da purps

    m_pos = convert_abs_to_screen ((0,0))
    center_x = m_pos[0] + 12 # I don't know why I have to offset the center x/y, but if I don't it is .. offset!
    center_y = m_pos[1] - 12 # I don't know why I have to offset the center x/y, but if I don't it is .. offset!
    

    if show_current_location:
        if is_start:
            color = (0, 0, 255)  # red
        else:
            color = (0, 255, 0)  # green

        cv2.circle(diffed, (center_x, center_y - 12), 3, color, -1)

    fill_seed = (center_x, center_y)

    # Debug showing diff post circles
    # cv2.imshow('diffed', diffed)
    # cv2.waitKey(0)

    return diffed, fill_seed


def rotate_map(img, angle):
    img_center = tuple(np.array(img.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(img_center, angle, 1.0)
    result = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def map_get_features(diff):
    # sift = cv2.SIFT_create()
    # surf = cv2.SURF

    # Fast style?
    # fast = cv2.FastFeatureDetector_create()
    # fast.setNonmaxSuppression(0)
    # kp = fast.detect(img, None)
    # features = cv2.drawKeypoints(img, kp, None, color=(255, 0, 0))

    # ORB style?
    # orb = cv2.ORB_create()
    orb = cv2.ORB_create(nfeatures=7500, edgeThreshold=0, scoreType=cv2.ORB_FAST_SCORE)
    # orb = cv2.ORB_create(nfeatures=1500, edgeThreshold=0, scoreType=cv2.ORB_FAST_SCORE)
    keypoints, descriptors = orb.detectAndCompute(diff, None)
    # features = cv2.drawKeypoints(diff, keypoints, None, color=(255, 0, 0))

    # Debug showing features
    # cv2.imshow('Features', features)
    # cv2.waitKey(0)

    return keypoints, descriptors


def map_merge_features(diff_1, diff_2):
    keypoints_1, descriptors_1 = map_get_features(diff_1)
    keypoints_2, descriptors_2 = map_get_features(diff_2)

    # Debug showing keypoints
    # cv2.imshow("Result", cv2.drawKeypoints(diff_1, keypoints_1, None, color=(255, 0, 0)))
    # cv2.waitKey(0)
    # cv2.imshow("Result", cv2.drawKeypoints(diff_2, keypoints_2, None, color=(255, 0, 0)))
    # cv2.waitKey(0)

    # *** BF MATCHER OLD
    # Match descriptors between images
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors_1, descriptors_2)

    # Debug outputting first 10 matches sorted by dist
    # matches = sorted(matches, key=lambda x: x.distance)
    # img3 = cv2.drawMatches(diff_1, keypoints_1, diff_2, keypoints_2, matches[:10], None, flags=2)
    # cv2.imshow("Result", img3)
    # cv2.waitKey(0)

    # Extract location of good matches (wtf are good matches?!)
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points1[i, :] = keypoints_1[match.queryIdx].pt
        points2[i, :] = keypoints_2[match.trainIdx].pt

    # # *** Flann matcher
    # Match descriptors between images
    # FLANN_INDEX_LSH = 6
    # index_params = dict(
    #     algorithm=FLANN_INDEX_LSH,
    #     table_number=12,  # 12
    #     key_size=20,  # 20
    #     multi_probe_level=2,  # 2
    # )
    # flann = cv2.FlannBasedMatcher(index_params, {"checks": 50})
    # matches = flann.knnMatch(descriptors_1, descriptors_2, k=2)
    #
    # # ratio test as per Lowe's paper
    # points1 = np.zeros((len(matches), 2), dtype=np.float32)
    # points2 = np.zeros((len(matches), 2), dtype=np.float32)
    # for i, (m, n) in enumerate(matches):
    #     if m.distance < 0.7 * n.distance:
    #         points1[i, :] = keypoints_1[m.queryIdx].pt
    #         points2[i, :] = keypoints_2[m.trainIdx].pt


    # This works...
    H, mask = cv2.estimateAffine2D(points2, points1)
    # H, mask = cv2.estimateAffinePartial2D(points1, points2)  # ??? don't think we need this? doesn't seem to work
    original_with_padding, new_with_padding = warpAffinePadded(diff_2, diff_1, H, flags=cv2.INTER_NEAREST)
    # original_with_padding, new_with_padding = warpAffinePadded(diff_2, diff_1, H, flags=cv2.INTER_LANCZOS4)  # slow ?
    # original_with_padding, new_with_padding = warpAffinePadded(diff_2, diff_1, H, flags=cv2.INTER_CUBIC)  # worked OK?
    # original_with_padding, new_with_padding = warpAffinePadded(diff_2, diff_1, H, flags=cv2.INTER_NEAREST_EXACT)

    # Debug showing padding results
    # cv2.imshow("new_with_padding", new_with_padding)
    # cv2.imshow("original_with_padding", original_with_padding)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Let's find red starting point, which may be overwritten by waypoints/other things
    # so we can highlight over it again later
    red_starting_point_mask = np.all(original_with_padding == [0, 0, 255], axis=-1)

    # Delete any old green markers for "current location"
    original_with_padding[np.all(original_with_padding == [0, 255, 0], axis=-1)] = [0, 0, 0]

    # Take black areas from newest diff and override old white areas in old image  # TODO: make this a mode for areas we're taking MANY shots in?
    # original_with_padding[np.all(original_with_padding == [127, 127, 127], axis=-1)] = [0, 0, 0]  # anything that was gray -> remove it, black now
    # original_with_padding[np.all(new_with_padding == [0, 0, 0], axis=-1)] = [127, 127, 127]  # anything black in new image -> gray, prepped to be removed if not repeated

    # Merge original with new
    # map = cv2.bitwise_or(original_with_padding, new_with_padding)
    map = cv2.bitwise_or(new_with_padding, original_with_padding)  # TODO: trying to swap ordering??
    # map = cv2.bitwise_or(new_with_padding, original_with_padding, mask=new_with_padding[np.all(new_with_padding == [0, 0, 0])])
    # map = cv2.bitwise_and(new_with_padding, original_with_padding, mask=excluding areas in padding or something?)


    # TODO: Merge together AND the overlapping areas, but OR on areas not overlapping ??

    # Re-add red mask so it's super clear
    map[red_starting_point_mask] = [0, 0, 255]

    # where are we? if we're right on the red X, that'd be (10_000, 10_000)
    # # green_current_point_mask = np.all(map == [0, 255, 0], axis=-1)
    # green_current_point_mask = np.any(map == [0, 255, 0], axis=-1)
    # # M = cv2.moments(green_current_point_mask)
    # # cX = int(M["m10"] / M["m00"])
    # # cY = int(M["m01"] / M["m00"])
    # # print(cX, cY)
    # import pdb; pdb.set_trace()
    # coordinates = list(zip(green_current_point_mask[0], green_current_point_mask[1]))
    # print(green_current_point_mask)
    # print(coordinates)

    # Look in original image for red coordinate
    # red_coords = np.where(np.all(map == [0, 0, 255], axis=-1))
    # red_coords = np.transpose(red_coords)  # faster than 'zip' but does same thing ???
    # red_y, red_x = red_coords[0]
    red_x, red_y = map_get_coordinates(map, [0, 0, 255])

    try:
        green_coords = np.where(np.all(new_with_padding == [0, 255, 0], axis=-1))
        green_coords = np.transpose(green_coords)  # faster than 'zip' but does same thing ???
        green_y, green_x = green_coords[0]
    except IndexError:
        raise ValueError("Could not find green marker indicating current position") from None

    # red is start at 10_000, 10_000 so base it off that...
    current_x, current_y = 10_000 + green_x - red_x, 10_000 + green_y - red_y

    base_x, base_y = red_x, red_y

    # Debug showing final map!!!
    # cv2.imshow("Result", map)
    # cv2.waitKey(0)
    return map, current_x, current_y, base_x, base_y


def map_get_coordinates(map, color):
    coords = np.where(np.all(map == color, axis=-1))
    coords = np.transpose(coords)  # faster than 'zip' but does same thing ???
    y, x = coords[0]
    return x, y


def map_process():
    """"""
    pass


def flood_fill(img, seed_point):
    """Perform a single flood fill operation.
    # Arguments
        img: an image. the image should consist of black background, white lines and white fills.
               the black area is unfilled area, and the white area is filled area.
        seed_point: seed point for trapped-ball fill, a tuple (integer, integer).
    # Returns
        an image after filling.
    """
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    flooded_img = np.full(img.shape, 255, np.uint8)

    mask1 = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_CONSTANT, 0)
    _, flooded_img, _, _ = cv2.floodFill(flooded_img, mask1, seed_point, 0, 1, 1, 4) #green is the seed_point color

    return flooded_img 


"""Padded transformation module.
This module provides two functions, warpPerspectivePadded() and
warpAffinePadded(), which compliment the built-in OpenCV functions
warpPerspective() and warpAffine(). These functions calculate the
extent of the warped image and pads both the destination and the
warped image so both images can be fully displayed together.
References
----------
See the following question and my answer on Stack Overflow for an
idea of how this was conceptualized and to read the mathematics
behind the functions: https://stackoverflow.com/a/44459869/5087436
"""

def warpPerspectivePadded(
        src, dst, M,
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0):
    """Performs a perspective warp with padding.
    Parameters
    ----------
    src : array_like
        source image, to be warped.
    dst : array_like
        destination image, to be padded.
    M : array_like
        `3x3` perspective transformation matrix.

    Returns
    -------
    src_warped : ndarray
        padded and warped source image
    dst_padded : ndarray
        padded destination image, same size as src_warped

    Optional Parameters
    -------------------
    flags : int, optional
        combination of interpolation methods (`cv2.INTER_LINEAR` or
        `cv2.INTER_NEAREST`) and the optional flag `cv2.WARP_INVERSE_MAP`,
        that sets `M` as the inverse transformation (`dst` --> `src`).
    borderMode : int, optional
        pixel extrapolation method (`cv2.BORDER_CONSTANT` or
        `cv2.BORDER_REPLICATE`).
    borderValue : numeric, optional
        value used in case of a constant border; by default, it equals 0.

    See Also
    --------
    warpAffinePadded() : for `2x3` affine transformations
    cv2.warpPerspective(), cv2.warpAffine() : original OpenCV functions
    """

    assert M.shape == (3, 3), \
        'Perspective transformation shape should be (3, 3).\n' \
        + 'Use warpAffinePadded() for (2, 3) affine transformations.'

    M = M / M[2, 2]  # ensure a legal homography
    if flags in (cv2.WARP_INVERSE_MAP,
                 cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                 cv2.INTER_NEAREST + cv2.WARP_INVERSE_MAP):
        M = cv2.invert(M)[1]
        flags -= cv2.WARP_INVERSE_MAP

    # it is enough to find where the corners of the image go to find
    # the padding bounds; points in clockwise order from origin
    src_h, src_w = src.shape[:2]
    lin_homg_pts = np.array([
        [0, src_w, src_w, 0],
        [0, 0, src_h, src_h],
        [1, 1, 1, 1]
    ])

    # transform points
    transf_lin_homg_pts = M.dot(lin_homg_pts)
    transf_lin_homg_pts /= transf_lin_homg_pts[2, :]

    # find min and max points
    min_x = np.floor(np.min(transf_lin_homg_pts[0])).astype(int)
    min_y = np.floor(np.min(transf_lin_homg_pts[1])).astype(int)
    max_x = np.ceil(np.max(transf_lin_homg_pts[0])).astype(int)
    max_y = np.ceil(np.max(transf_lin_homg_pts[1])).astype(int)

    # add translation to the transformation matrix to shift to positive values
    anchor_x, anchor_y = 0, 0
    transl_transf = np.eye(3, 3)
    if min_x < 0:
        anchor_x = -min_x
        transl_transf[0, 2] += anchor_x
    if min_y < 0:
        anchor_y = -min_y
        transl_transf[1, 2] += anchor_y
    shifted_transf = transl_transf.dot(M)
    shifted_transf /= shifted_transf[2, 2]

    # create padded destination image
    dst_h, dst_w = dst.shape[:2]
    pad_widths = [
        anchor_y, max(max_y, dst_h) - dst_h,
        anchor_x, max(max_x, dst_w) - dst_w
    ]

    dst_padded = cv2.copyMakeBorder(dst, *pad_widths, borderType=borderMode, value=borderValue)
    dst_pad_h, dst_pad_w = dst_padded.shape[:2]
    src_warped = cv2.warpPerspective(src, shifted_transf, (dst_pad_w, dst_pad_h), flags=flags, borderMode=borderMode, borderValue=borderValue)
    return dst_padded, src_warped


def warpAffinePadded(src, dst, M, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0):
    """Performs an affine or Euclidean/rigid warp with padding.
    Parameters
    ----------
    src : array_like
        source image, to be warped.
    dst : array_like
        destination image, to be padded.
    M : array_like
        `2x3` affine transformation matrix.
    Returns
    -------
    src_warped : ndarray
        padded and warped source image
    dst_padded : ndarray
        padded destination image, same size as src_warped
    Optional Parameters
    -------------------
    flags : int, optional
        combination of interpolation methods (`cv2.INTER_LINEAR` or
        `cv2.INTER_NEAREST`) and the optional flag `cv2.WARP_INVERSE_MAP`,
        that sets `M` as the inverse transformation (`dst` --> `src`).
    borderMode : int, optional
        pixel extrapolation method (`cv2.BORDER_CONSTANT` or
        `cv2.BORDER_REPLICATE`).
    borderValue : numeric, optional
        value used in case of a constant border; by default, it equals 0.
    See Also
    --------
    warpPerspectivePadded() : for `3x3` perspective transformations
    cv2.warpPerspective(), cv2.warpAffine() : original OpenCV functions
    """
    assert M.shape == (2, 3), \
        'Affine transformation shape should be (2, 3).\n' \
        + 'Use warpPerspectivePadded() for (3, 3) homography transformations.'

    if flags in (cv2.WARP_INVERSE_MAP,
                 cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                 cv2.INTER_NEAREST + cv2.WARP_INVERSE_MAP):
        M = cv2.invertAffineTransform(M)
        flags -= cv2.WARP_INVERSE_MAP

    # it is enough to find where the corners of the image go to find
    # the padding bounds; points in clockwise order from origin
    src_h, src_w = src.shape[:2]
    lin_pts = np.array([
        [0, src_w, src_w, 0],
        [0, 0, src_h, src_h]
    ])

    # transform points
    transf_lin_pts = M[:, :2].dot(lin_pts) + M[:, 2].reshape(2, 1)

    # find min and max points
    min_x = np.floor(np.min(transf_lin_pts[0])).astype(int)
    min_y = np.floor(np.min(transf_lin_pts[1])).astype(int)
    max_x = np.ceil(np.max(transf_lin_pts[0])).astype(int)
    max_y = np.ceil(np.max(transf_lin_pts[1])).astype(int)

    # add translation to the transformation matrix to shift to positive values
    anchor_x, anchor_y = 0, 0
    if min_x < 0:
        anchor_x = -min_x
    if min_y < 0:
        anchor_y = -min_y
    shifted_transf = M + [[0, 0, anchor_x], [0, 0, anchor_y]]

    # if np.any(shifted_transf >= 4) or np.any(shifted_transf <= -4):
    #     raise ImageMergeException("We way outta da bounds!")

    if anchor_x >= 200 or anchor_y >= 200:
        raise ValueError("It seems like we had a bad stitch? try again, maybe someone walked in front of minimap?")

    # create padded destination image
    dst_h, dst_w = dst.shape[:2]

    pad_widths = [anchor_y, max(max_y, dst_h) - dst_h,
                  anchor_x, max(max_x, dst_w) - dst_w]

    dst_padded = cv2.copyMakeBorder(dst, *pad_widths, borderType=borderMode, value=borderValue)

    dst_pad_h, dst_pad_w = dst_padded.shape[:2]


    # TODO: check old width vs new width, are we increasing > 10%?

    print("are we doing a huge shift here?")
    print(shifted_transf)
    print("anchors:", anchor_x, anchor_y)
    print("src_h, src_w:", src_h, src_w)
    print("pad h,w:", dst_pad_h, dst_pad_w)


    src_warped = cv2.warpAffine(src, shifted_transf, (dst_pad_w, dst_pad_h), flags=flags, borderMode=borderMode, borderValue=borderValue)

    return dst_padded, src_warped

# Testing: Have whatever you want to find on the screen
if __name__ == "__main__":
    import keyboard
    from screen import start_detecting_window, stop_detecting_window, convert_abs_to_monitor
    from utils.misc import wait
    import template_finder
    from pather import Pather
    
    print("Press f11 to start, Press F12 to exit")
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    keyboard.wait("f11")

    start_detecting_window()
    from config import Config
    from char.sorceress import LightSorc
    from char.paladin.hammerdin import Hammerdin
    from item.pickit import PickIt
    from automap_finder import toggle_automap
    from utils.misc import color_filter
    pather = Pather()

    char = Hammerdin(Config().hammerdin, pather, PickIt) #Config().char,
    char.discover_capabilities()

    while 1:
        pre, during_1, during_2 = map_capture() # take screenshots
        diff_1, fill_seed = map_diff(pre, during_1, during_2, is_start=False, show_current_location=True, threshold=0.11) #make the diff & spit out the map
        #cv2.imshow('final_img', final_img)

        scaled = cv2.resize(diff_1, dsize=None, fx=0.55, fy=1.1, interpolation=cv2.INTER_LINEAR)
        final_img = rotate_map(scaled, 45)
        #cv2.imshow('final_img', final_img)
        #cv2.waitKey(0)

        #fill_seed = (0,0)
        #final_img = flood_fill(final_img, fill_seed)

        #final_img = color_filter(final_img, Config().colors["stony_field_map"])

        cv2.imshow('final_img', final_img)
        key = cv2.waitKey(1)
        #keyboard.wait("f12")
    
    #TODO: 
    # - flood fill the walkable path
    # - stitch together map parts whilst exploring to generate global coordinates
    
    #stitch a map

    #Logger.debug("Wait 5s, use the time to move a bit!")
    #wait(5)
    #pre, during_1, during_2 = map_capture() # take screenshots
    #diff_2 = map_diff(pre, during_1, during_2, is_start=False, show_current_location=True, threshold=0.11) #make the diff & spit out the map 
    #keypoints, descriptors = map_get_features(diff_1)
    #keypoints, descriptors = map_get_features(diff_2)
    #map, current_x, current_y, base_x, base_y = map_merge_features(diff_1, diff_2)
    #x, y = map_get_coordinates (map, color)
    #cv2.imshow('final_img', map)
    #cv2.waitKey(0)
