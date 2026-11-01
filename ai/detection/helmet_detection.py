import cv2
from ultralytics import YOLO
from database.helmet import helmet_store


# Load helmet detection model once
helmet_model = YOLO("helmet_model.pt")


def detect_helmets(frame,vehical_id,cam_id, confidence=0.40):
    """
    Detect helmets in a single video frame.

    Returns:
        frame: frame with helmet detections drawn
        helmets: list of detected helmets
    """

    results = helmet_model.predict(
        source=frame,
        imgsz=640,
        conf=confidence,
        verbose=False
    )

    result = results[0]

    helmets = []

    for box in result.boxes:

        # Bounding box
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        # Confidence
        conf = float(box.conf[0])

        # Class
        class_id = int(box.cls[0])
        class_name = helmet_model.names[class_id]

        helmet = {
            "class": class_name,
            "vehical_id": vehical_id , 
            "camera_id": cam_id,
            "helmetframe": frame[y1:y2 ,x1:x2],
            "confidence": conf,
            "bbox": [
                int(x1),
                int(y1),
                int(x2),
                int(y2)
            ]
        }
        helmet_id = helmet_store(frame,vehical_id,cam_id)
        helmet.insert[{"helmet_id":helmet_id}] 

        helmets.append(helmet)

        # Draw box
        cv2.rectangle(
            frame,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            (0, 255, 0),
            2
        )

        # Label
        label = f"{class_name} {conf:.2f}"

        cv2.putText(
            frame,
            label,
            (int(x1), int(y1) - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    return frame, helmets