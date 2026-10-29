import cv2


def filter_frame(frame, size=(640, 640)):
    # Resize
    frame = cv2.resize(
        frame,
        size,
        interpolation=cv2.INTER_LANCZOS4
    )

    # Improve contrast
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    l = clahe.apply(l)

    frame = cv2.merge((l, a, b))
    frame = cv2.cvtColor(frame, cv2.COLOR_LAB2BGR)

    # Light sharpening
    blurred = cv2.GaussianBlur(frame, (0, 0), 1)

    frame = cv2.addWeighted(
        frame,
        1.2,
        blurred,
        -0.2,
        0
    )

    return frame


