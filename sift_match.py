import cv2
import numpy as np

# ============================================================
# 1. LOAD IMAGES
# ============================================================

image1 = cv2.imread("images/image1.jpg")
image2 = cv2.imread("images/image2.jpg")

if image1 is None:
    print("Could not load image1.jpg")
    exit()

if image2 is None:
    print("Could not load image2.jpg")
    exit()

print("Images loaded successfully!")

print("Image 1 dimensions:", image1.shape)
print("Image 2 dimensions:", image2.shape)


# ============================================================
# 2. CONVERT TO GRAYSCALE
# ============================================================

gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)


# ============================================================
# 3. CREATE SIFT DETECTOR
# ============================================================

sift = cv2.SIFT_create(
    nfeatures=5000,
    nOctaveLayers=4,
    contrastThreshold=0.025,
    edgeThreshold=10,
    sigma=1.6
)


# ============================================================
# 4. DETECT KEYPOINTS AND DESCRIPTORS
# ============================================================

kp1, des1 = sift.detectAndCompute(gray1, None)
kp2, des2 = sift.detectAndCompute(gray2, None)

print()
print("Keypoints image 1:", len(kp1))
print("Keypoints image 2:", len(kp2))

if des1 is None or des2 is None:
    print("Could not calculate descriptors.")
    exit()


# ============================================================
# 5. FLANN MATCHER
# ============================================================

FLANN_INDEX_KDTREE = 1

index_params = {
    "algorithm": FLANN_INDEX_KDTREE,
    "trees": 10
}

search_params = {
    "checks": 500
}

flann = cv2.FlannBasedMatcher(
    index_params,
    search_params
)


# ============================================================
# 6. FORWARD MATCHING
# IMAGE 1 → IMAGE 2
# ============================================================

forward_matches = flann.knnMatch(
    des1,
    des2,
    k=2
)


# ============================================================
# 7. BACKWARD MATCHING
# IMAGE 2 → IMAGE 1
# ============================================================

backward_matches = flann.knnMatch(
    des2,
    des1,
    k=2
)


# ============================================================
# 8. LOWE RATIO TEST
# ============================================================

ratio = 0.65

forward_good = {}

for pair in forward_matches:

    if len(pair) < 2:
        continue

    m, n = pair

    if m.distance < ratio * n.distance:
        forward_good[m.queryIdx] = m


backward_good = {}

for pair in backward_matches:

    if len(pair) < 2:
        continue

    m, n = pair

    if m.distance < ratio * n.distance:
        backward_good[m.queryIdx] = m


print()
print("Matches after ratio test:", len(forward_good))


# ============================================================
# 9. MUTUAL MATCHING
# ============================================================

mutual_matches = []

for idx1, match in forward_good.items():

    idx2 = match.trainIdx

    if idx2 in backward_good:

        reverse_match = backward_good[idx2]

        if reverse_match.trainIdx == idx1:
            mutual_matches.append(match)


print("Mutual matches:", len(mutual_matches))


# ============================================================
# 10. SORT MATCHES BY QUALITY
# ============================================================

mutual_matches = sorted(
    mutual_matches,
    key=lambda x: x.distance
)


# Limit candidates
MAX_CANDIDATES = 500

candidate_matches = mutual_matches[:MAX_CANDIDATES]

print("Candidates for geometry:", len(candidate_matches))


# ============================================================
# 11. CHECK WHETHER ENOUGH MATCHES EXIST
# ============================================================

if len(candidate_matches) < 4:

    print()
    print("ERROR: Not enough matches for homography.")
    print("Try adjusting the SIFT or ratio-test parameters.")
    exit()


# ============================================================
# 12. EXTRACT MATCHING POINTS
# ============================================================

src_pts = np.float32([
    kp1[m.queryIdx].pt
    for m in candidate_matches
]).reshape(-1, 1, 2)

dst_pts = np.float32([
    kp2[m.trainIdx].pt
    for m in candidate_matches
]).reshape(-1, 1, 2)


# ============================================================
# 13. FIND HOMOGRAPHY USING RANSAC
# ============================================================

H, mask = cv2.findHomography(
    src_pts,
    dst_pts,
    cv2.RANSAC,
    3.0,
    maxIters=5000,
    confidence=0.995
)


if H is None:

    print()
    print("Homography could not be calculated.")
    exit()


# ============================================================
# 14. EXTRACT RANSAC INLIERS
# ============================================================

mask = mask.ravel()

final_matches = [
    candidate_matches[i]
    for i in range(len(candidate_matches))
    if mask[i] == 1
]


# ============================================================
# 15. MATCH STATISTICS
# ============================================================

total_candidates = len(candidate_matches)
total_inliers = len(final_matches)

inlier_ratio = (
    total_inliers / total_candidates
    if total_candidates > 0
    else 0
)

print()
print("================ MATCH RESULTS ================")
print("Keypoints image 1:", len(kp1))
print("Keypoints image 2:", len(kp2))
print("Ratio-test matches:", len(forward_good))
print("Mutual matches:", len(mutual_matches))
print("RANSAC candidates:", total_candidates)
print("Final valid matches:", total_inliers)
print(f"Inlier ratio: {inlier_ratio:.2%}")


# ============================================================
# 16. CALCULATE REPROJECTION ERROR
# ============================================================

projected_points = cv2.perspectiveTransform(
    src_pts,
    H
)

errors = np.linalg.norm(
    projected_points - dst_pts,
    axis=2
).ravel()


inlier_errors = errors[mask == 1]


if len(inlier_errors) > 0:

    mean_error = np.mean(inlier_errors)
    max_error = np.max(inlier_errors)
    median_error = np.median(inlier_errors)

    print()
    print("================ GEOMETRIC ACCURACY ================")
    print(f"Mean reprojection error:   {mean_error:.2f} pixels")
    print(f"Median reprojection error: {median_error:.2f} pixels")
    print(f"Maximum reprojection error: {max_error:.2f} pixels")


# ============================================================
# 17. DRAW ONLY VERIFIED MATCHES
# ============================================================

matched_image = cv2.drawMatches(
    image1,
    kp1,
    image2,
    kp2,
    final_matches,
    None,
    flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
)

cv2.imwrite(
    "final_matches.jpg",
    matched_image
)

print()
print("Saved: final_matches.jpg")


# ============================================================
# 18. DRAW KEYPOINTS
# ============================================================

keypoints_image1 = cv2.drawKeypoints(
    image1,
    kp1,
    None,
    flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
)

keypoints_image2 = cv2.drawKeypoints(
    image2,
    kp2,
    None,
    flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
)

cv2.imwrite(
    "keypoints_image1.jpg",
    keypoints_image1
)

cv2.imwrite(
    "keypoints_image2.jpg",
    keypoints_image2
)

print("Saved: keypoints_image1.jpg")
print("Saved: keypoints_image2.jpg")


# ============================================================
# 19. ALIGN IMAGE 1 TO IMAGE 2
# ============================================================

height2, width2 = image2.shape[:2]

aligned_image = cv2.warpPerspective(
    image1,
    H,
    (width2, height2)
)

cv2.imwrite(
    "aligned_image.jpg",
    aligned_image
)

print("Saved: aligned_image.jpg")


# ============================================================
# 20. CREATE OVERLAY
# ============================================================

# Blend aligned image with image 2
overlay = cv2.addWeighted(
    aligned_image,
    0.5,
    image2,
    0.5,
    0
)

cv2.imwrite(
    "alignment_overlay.jpg",
    overlay
)

print("Saved: alignment_overlay.jpg")


# ============================================================
# 21. CREATE DIFFERENCE IMAGE
# ============================================================

aligned_gray = cv2.cvtColor(
    aligned_image,
    cv2.COLOR_BGR2GRAY
)

gray2_for_difference = cv2.cvtColor(
    image2,
    cv2.COLOR_BGR2GRAY
)


difference = cv2.absdiff(
    aligned_gray,
    gray2_for_difference
)


# Improve visibility of differences
difference = cv2.normalize(
    difference,
    None,
    0,
    255,
    cv2.NORM_MINMAX
)


cv2.imwrite(
    "difference.jpg",
    difference
)

print("Saved: difference.jpg")


# ============================================================
# 22. FINISHED
# ============================================================

print()
print("================================================")
print("             PROCESS COMPLETE")
print("================================================")