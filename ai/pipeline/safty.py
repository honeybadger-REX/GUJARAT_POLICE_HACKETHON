# safety_pipeline.py

from accident_detection import detect_accidents
from face_detection import detect_faces
from face_recognition import recognize_face


def safety_pipeline(
    frame,
    known_encodings,
    known_names
):

    # --------------------------------
    # ACCIDENT DETECTION
    # --------------------------------

    frame, accidents = detect_accidents(frame)


    # --------------------------------
    # NO ACCIDENT
    # --------------------------------

    if not accidents:
        return frame


    # --------------------------------
    # ACCIDENT FOUND
    # --------------------------------

    frame, faces = detect_faces(frame)


    # --------------------------------
    # FIND PEOPLE
    # --------------------------------

    for face in faces:

        name = recognize_face(
            face["encoding"],
            known_encodings,
            known_names
        )


        # --------------------------------
        # CREATE ALERT
        # --------------------------------

        create_alert(
            accidents=accidents,
            face=face,
            name=name
        )


    return frame


def create_alert(accidents, face, name):

    print("================================")
    print("🚨 ACCIDENT ALERT")
    print("Person:", name)
    print("Face:", face)
    print("Accident:", accidents)
    print("================================")
    