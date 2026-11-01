# vehicle_pipeline.py

from detection.vehicle_detection import detect_vehicles
from detection.helmet_detection import detect_helmets
from detection.face_detectiona_and_recognition import detect_faces
from detection.face_detectiona_and_recognition import recognize_face
from database.face import face_storage
from database.frame import frame_storage


def vehicle_pipeline(
    frame,
    known_encodings,
    known_names,cam_id
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

            vehicle_crop = vehicle["vehicleframe"]
            vehical_id = vehicle["vehicale_id"]


            # --------------------------------
            # HELMET DETECTION
            # --------------------------------

            vehicle_crop, helmet_result = detect_helmets(
                vehicle_crop ,vehical_id,cam_id
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

                frame, faces ,face= detect_faces(frame)


                for facez in faces:

                    name = recognize_face(
                        facez["encoding"],
                        known_encodings,
                        known_names
                    )
                    face_storage(name)

                


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

