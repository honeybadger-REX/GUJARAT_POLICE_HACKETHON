# vehicle_pipeline.py

from vehicle_detection import detect_vehicles
from helmet_detection import detect_helmets
from face_detection import detect_faces
from face_recognition import recognize_face


def vehicle_pipeline(
    frame,
    known_encodings,
    known_names
):
    """
    Process vehicles found in one frame.
    """

    # --------------------------------
    # VEHICLE DETECTION
    # --------------------------------

    frame, vehicles = detect_vehicles(frame)


    # --------------------------------
    # PROCESS EACH VEHICLE
    # --------------------------------

    for vehicle in vehicles:

        vehicle_type = vehicle["class"]


        # =================================
        # TWO WHEELER
        # =================================

        if vehicle_type == "2-wheeler":

            x1, y1, x2, y2 = vehicle["bbox"]

            vehicle_crop = frame[
                y1:y2,
                x1:x2
            ]


            # --------------------------------
            # HELMET DETECTION
            # --------------------------------

            vehicle_crop, helmet_result = detect_helmets(
                vehicle_crop
            )


            # --------------------------------
            # HELMET PRESENT
            # --------------------------------

            if helmet_result:

                store_vehicle(
                    vehicle=vehicle,
                    helmet=helmet_result
                )


            # --------------------------------
            # NO HELMET
            # --------------------------------

            else:

                frame, faces = detect_faces(frame)


                for face in faces:

                    name = recognize_face(
                        face["encoding"],
                        known_encodings,
                        known_names
                    )


                    record_face(
                        vehicle=vehicle,
                        face=face,
                        name=name
                    )


        # =================================
        # THREE / FOUR WHEELER
        # =================================

        elif vehicle_type in [
            "3-wheeler",
            "4-wheeler"
        ]:

            store_vehicle(vehicle)


    return frame


# =================================
# DATABASE FUNCTIONS
# =================================

def store_vehicle(vehicle, helmet=None):

    print(
        "STORE VEHICLE:",
        vehicle,
        "HELMET:",
        helmet
    )


def record_face(vehicle, face, name):

    print(
        "RECORD FACE:",
        name,
        "VEHICLE:",
        vehicle
    )