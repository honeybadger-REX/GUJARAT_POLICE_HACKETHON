import cv2
import asyncio

from concurrent.futures import ThreadPoolExecutor

from pipeline.image_filter import filter_frame
from pipeline.vehicle import vehicle_pipeline
from pipeline.safety import safety_pipeline


# =================================
# KNOWN PEOPLE
# =================================

known_encodings = []
known_names = []


# =================================
# THREAD POOL
# =================================

executor = ThreadPoolExecutor(max_workers=2)


# =================================
# ASYNC SAFETY PIPELINE
# =================================

async def run_safety(
    frame,
    loop
):

    return await loop.run_in_executor(
        executor,
        safety_pipeline,
        frame,
        known_encodings,
        known_names
    )


# =================================
# ASYNC VEHICLE PIPELINE
# =================================

async def run_vehicle(
    frame,
    loop
):

    return await loop.run_in_executor(
        executor,
        vehicle_pipeline,
        frame,
        known_encodings,
        known_names
    )


# =================================
# MAIN ASYNC PIPELINE
# =================================

async def main_pipeline(video_source,camera_id):

    cap = cv2.VideoCapture(video_source)

    loop = asyncio.get_running_loop()

    while cap.isOpened():

        # --------------------------------
        # READ FRAME
        # --------------------------------

        ret, frame = cap.read()

        if not ret:
            break


        # --------------------------------
        # FILTER
        # --------------------------------

        frame, camera_id , frame_id = filter_frame(frame)


        # --------------------------------
        # CREATE TWO TASKS
        # --------------------------------

        safety_task = asyncio.create_task(
            run_safety(
                frame.copy(),
                loop
            )
        )

        vehicle_task = asyncio.create_task(
            run_vehicle(
                frame.copy(),
                loop
            )
        )


        # --------------------------------
        # WAIT FOR BOTH
        # --------------------------------

        safety_frame, vehicle_frame = await asyncio.gather(
            safety_task,
            vehicle_task
        )


        # --------------------------------
        # DISPLAY
        # --------------------------------

        cv2.imshow(
            "Gujarat Police Surveillance",
            safety_frame
        )


        # --------------------------------
        # EXIT
        # --------------------------------

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    cap.release()
    cv2.destroyAllWindows()


# =================================
# START
# =================================

if __name__ == "__main__":

    asyncio.run(
        main_pipeline("test_video.mp4")
    )