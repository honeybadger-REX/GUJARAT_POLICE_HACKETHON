import cv2
import face_recognition
import face_recognition


def detect_faces(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    locations = face_recognition.face_locations(rgb_frame)
    encodings = face_recognition.face_encodings(
        rgb_frame,
        locations
    )

    faces = []

    for location, encoding in zip(locations, encodings):

        top, right, bottom, left = location

        face = {
            "encoding": encoding,
            "bbox": [left, top, right, bottom]
        }

        faces.append(face)

        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (255, 0, 0),
            2
        )

    return frame, faces






def recognize_face(face_encoding, known_encodings, known_names, tolerance=0.50):

    if len(known_encodings) == 0:
        return "Unknown"

    matches = face_recognition.compare_faces(
        known_encodings,
        face_encoding,
        tolerance=tolerance
    )

    distances = face_recognition.face_distance(
        known_encodings,
        face_encoding
    )

    best_match = distances.argmin()

    if matches[best_match]:
        return known_names[best_match]

    return "Unknown"