from ultralytics import YOLO
import cv2
import uuid

# Load model once
helmet_model = YOLO("best.pt")


def detect_helmet(frame, camera_id, frame_id, confidence=0.40):

    results = helmet_model.predict(
        source=frame,
        imgsz=640,
        conf=confidence,
        verbose=False
    )

    result = results[0]
    helmets = []

    # Preserve the original frame for clean crops
    original_frame = frame.copy()

    height, width = frame.shape[:2]

    for box in result.boxes:

        # Bounding box
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        # Keep coordinates inside the image
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(width, x2)
        y2 = min(height, y2)

        conf = float(box.conf[0])

        class_id = int(box.cls[0])
        class_name = helmet_model.names[class_id]

        # Crop this individual vehicle
        helmet_frame = original_frame[y1:y2, x1:x2].copy()

        helmet = {
            "detection_id": str(uuid.uuid4()),
            "camera_id": camera_id,
            "frame_id": frame_id,
            "class": class_name,
            "confidence": conf,
            "bbox": [x1, y1, x2, y2],

            # Temporary image for downstream detection
            "helemt_frame": helmet_frame
        }

        helmets.append(helmet)

        # Draw bounding box
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        label = f"{class_name} {conf:.2f}"

        cv2.putText(
            frame,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    return frame, helmets