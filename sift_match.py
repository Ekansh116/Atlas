import cv2

# Load the two images
image1 = cv2.imread("images/image1.jpg")
image2 = cv2.imread("images/image2.jpg")

# Check whether the images were loaded
if image1 is None:
    print("Could not load image1.jpg")
    exit()

if image2 is None:
    print("Could not load image2.jpg")
    exit()

print("Image 1 loaded successfully!")
print("Image 2 loaded successfully!")

print("Image 1 dimensions:", image1.shape)
print("Image 2 dimensions:", image2.shape)


# Convert images to grayscale
gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

print("Grayscale Image 1 dimensions:", gray1.shape)
print("Grayscale Image 2 dimensions:", gray2.shape)

# Create SIFT detector
sift = cv2.SIFT_create()

# Detect keypoints and compute descriptors
keypoints1, descriptors1 = sift.detectAndCompute(gray1, None)
keypoints2, descriptors2 = sift.detectAndCompute(gray2, None)

print("Image 1 keypoints:", len(keypoints1))
print("Image 2 keypoints:", len(keypoints2))

print("Image 1 descriptor shape:", descriptors1.shape)
print("Image 2 descriptor shape:", descriptors2.shape)

# Create a Brute-Force matcher
bf = cv2.BFMatcher()

# Match descriptors between the two images
matches = bf.knnMatch(descriptors1, descriptors2, k=2)

print("Number of descriptor matches:", len(matches))

# Apply Lowe's ratio test
good_matches = []

for m, n in matches:
    if m.distance < 0.7 * n.distance:
        good_matches.append(m)

print("Good matches:", len(good_matches))

# Draw detected keypoints
keypoints_image1 = cv2.drawKeypoints(
    image1,
    keypoints1,
    None,
    flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
)

keypoints_image2 = cv2.drawKeypoints(
    image2,
    keypoints2,
    None,
    flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
)

# Save the results
cv2.imwrite("keypoints_image1.jpg", keypoints_image1)
cv2.imwrite("keypoints_image2.jpg", keypoints_image2)

print("Keypoint images saved!")

# Draw the good matches
matched_image = cv2.drawMatches(
    image1,
    keypoints1,
    image2,
    keypoints2,
    good_matches,
    None,
    flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
)

# Save the result
cv2.imwrite("sift_matches.jpg", matched_image)

print("Match visualization saved as sift_matches.jpg")