from vehicle_detection import detect_vehicles
from helmet_detection import detect_helmets
from face_detectiona_and_recognition import detect_faces, recognize_face


def vehicle_pipeline(
    frame,
    camera_id,
    frame_id,
    known_encodings=None,
    known_names=None
):
    """
    Process one frame through the vehicle pipeline.

    Flow:
        Vehicle Detection
              ↓
        2-wheeler?
          ↓        ↓
        YES        NO
         ↓          ↓
      Helmet      Store vehicle
         ↓
    No Helmet?
      ↓     ↓
    YES     NO
     ↓       ↓
    Face    Store vehicle
     ↓
    Recognition
     ↓
    Final vehicle result
    """

    # --------------------------------------------------
    # 1. Detect vehicles
    # --------------------------------------------------

    frame, vehicles = detect_vehicles(
        frame,
        camera_id,
        frame_id
    )

    final_vehicles = []

    # --------------------------------------------------
    # 2. Process every detected vehicle
    # --------------------------------------------------

    for vehicle in vehicles:

        vehicle_result = {
            "camera_id": camera_id,
            "frame_id": frame_id,
            "vehicle": {
                "class": vehicle["class"],
                "confidence": vehicle["confidence"],
                "bbox": vehicle["bbox"]
            },
            "helmet": None,
            "face": None,
            "event": None,
            "eveidnce":{
            "vehicle_frame" : frame,
            "helmet_frame":None,
            "face_frame":None  
                                    }
        }

        # Vehicle bounding box
        x1, y1, x2, y2 = vehicle["bbox"]

        # Crop vehicle from frame
        vehicle_frame = frame[y1:y2, x1:x2]

        # --------------------------------------------------
        # 3. Only check helmet for 2-wheelers
        # --------------------------------------------------

        if vehicle["class"] == "2-wheeler":

            helmets = detect_helmets(
                vehicle_frame,
                camera_id
            )

            # --------------------------------------------------
            # 4. Helmet found
            # --------------------------------------------------

            if len(helmets) > 0:

                best_helmet = max(
                    helmets,
                    key=lambda x: x["confidence"]
                )

                vehicle_result["helmet"] = {
                    "detected": True,
                    "confidence": best_helmet["confidence"],
                    "bbox": best_helmet["bbox"]
                }
                vehicle_result["eveidnce"] = {
                    "helmet_frame": best_helmet["frame"]

                }

            # --------------------------------------------------
            # 5. No helmet
            # --------------------------------------------------

            else:

                vehicle_result["helmet"] = {
                    "detected": False
                }
                vehicle_result["eveidnce"] = {
                "helmet_frame": best_helmet["frame"]}

                # Detect face inside vehicle crop
                faces = detect_faces(vehicle_frame)

                if len(faces) > 0:

                    face = faces[0]

                    vehicle_result["face"] = {
                        "bbox": face["bbox"]
                    }
                    vehicle_result["eveidnce"] = {
                    "face_frame": face["frame"]
                                                    }

                    # ------------------------------------------
                    # 6. Face recognition
                    # ------------------------------------------

                    if known_encodings and known_names:

                        recognition = recognize_face(
                            face["encoding"],
                            known_encodings,
                            known_names
                        )

                        vehicle_result["face"].update(
                            recognition
                        )

                    else:

                        vehicle_result["face"].update({
                            "person_id": None,
                            "name": "Unknown",
                            "status": "unknown"
                        })

                # ------------------------------------------
                # 7. Create event
                # ------------------------------------------

                vehicle_result["event"] = {
                    "type": "NO_HELMET"
                }

        # --------------------------------------------------
        # 8. Add vehicle result
        # --------------------------------------------------

        final_vehicles.append(vehicle_result)

    # --------------------------------------------------
    # 9. Return complete pipeline result
    # --------------------------------------------------

    return frame, {
        "camera_id": camera_id,
        "frame_id": frame_id,
        "vehicles": final_vehicles
    }