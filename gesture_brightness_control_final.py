import cv2
import numpy as np
import mediapipe as mp
import math

# Initialize MediaPipe Hands for hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Open webcam
cap = cv2.VideoCapture(0)

# Function to adjust brightness
def adjust_brightness(frame, brightness_value):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, brightness_value)
    v[v > 255] = 255
    v[v < 0] = 0
    final_hsv = cv2.merge((h, s, v))
    return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

# Main loop for processing the video feed
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a selfie-view display
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    
    # Convert the frame to RGB for MediaPipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    brightness_value = 0  # Default brightness adjustment value
    
    # If hand landmarks are detected
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the coordinates of the tip of the thumb and the tip of the index finger
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Convert the normalized coordinates to pixel values
            index_x, index_y = int(index_finger_tip.x * frame_width), int(index_finger_tip.y * frame_height)
            thumb_x, thumb_y = int(thumb_tip.x * frame_width), int(thumb_tip.y * frame_height)

            # Draw circles on the tip of index finger and thumb for visualization
            cv2.circle(frame, (index_x, index_y), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(frame, (thumb_x, thumb_y), 10, (255, 0, 0), cv2.FILLED)
            cv2.line(frame, (index_x, index_y), (thumb_x, thumb_y), (0, 255, 0), 2)

            # Calculate the distance between the index finger and thumb
            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)

            # Map the distance to a brightness value (-100 to 100)
            brightness_value = np.interp(distance, [30, 200], [-100, 100])

            # Display brightness value for testing
            cv2.putText(frame, f"Brightness: {int(brightness_value)}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Adjust the brightness of the frame based on the finger distance
    adjusted_frame = adjust_brightness(frame, int(brightness_value))

    cv2.imshow("Brightness Control", adjusted_frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
