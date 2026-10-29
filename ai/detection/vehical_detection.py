from ultralytics import YOLO
import cv2


# Load model once
vehicle_model = YOLO("best.pt")


def detect_vehicles(frame, confidence=0.40):
    """
    Detect vehicles in a single video frame.

    Returns:
        frame: frame with detection boxes and labels
        vehicles: list containing detected vehicle information
    """

    results = vehicle_model.predict(
        source=frame,
        imgsz=640,
        conf=confidence,
        verbose=False
    )

    result = results[0]

    vehicles = []

    for box in result.boxes:

        # Bounding box
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        # Confidence
        conf = float(box.conf[0])

        # Class
        class_id = int(box.cls[0])
        class_name = vehicle_model.names[class_id]

        # Store detection information
        vehicle = {
            "class": class_name,
            "confidence": conf,
            "bbox": [
                int(x1),
                int(y1),
                int(x2),
                int(y2)
            ]
        }

        vehicles.append(vehicle)

        # Draw bounding box
        cv2.rectangle(
            frame,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            (0, 255, 0),
            2
        )

        # Draw label
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

    return frame, vehicles