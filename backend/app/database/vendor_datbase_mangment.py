import mysql.connector
import subprocess


# ==========================================
# DATABASE CONNECTION
# ==========================================

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="gujarat_police"
)

cursor = conn.cursor()


# ==========================================
# VENDOR MANAGEMENT
# ==========================================

vendor_sql = """
INSERT INTO vendor (VendorName, NUMBER_CAM, URL, enable)
VALUES (%s, %s, %s, %s)
"""


def enter_vendor(name, number_cam, url, enable):

    values = (
        name,
        number_cam,
        url,
        enable
    )

    cursor.execute(vendor_sql, values)
    conn.commit()

    print("Vendor added successfully")


def remove_vendor(name):

    cursor.execute(
        "DELETE FROM vendor WHERE VendorName = %s",
        (name,)
    )

    conn.commit()

    print("Vendor removed successfully")


def update_vendor(name, number_cam=None, url=None, enable=None):

    if number_cam is not None:

        cursor.execute(
            """
            UPDATE vendor
            SET NUMBER_CAM = %s
            WHERE VendorName = %s
            """,
            (number_cam, name)
        )

    if url is not None:

        cursor.execute(
            """
            UPDATE vendor
            SET URL = %s
            WHERE VendorName = %s
            """,
            (url, name)
        )

    if enable is not None:

        cursor.execute(
            """
            UPDATE vendor
            SET enable = %s
            WHERE VendorName = %s
            """,
            (enable, name)
        )

    conn.commit()

    print("Vendor updated successfully")


# ==========================================
# CAMERA STATUS CHECK
# ==========================================

def check_camera(url):

    command = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", url,
        "-t", "3",
        "-f", "null",
        "-"
    ]

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )

        if result.returncode == 0:
            return "ONLINE"

        return "OFFLINE"

    except subprocess.TimeoutExpired:

        return "OFFLINE"


# ==========================================
# INSERT CAMERA
# ==========================================

camera_sql = """
INSERT INTO camera (CameraName, VendorID, CameraURL, enable)
VALUES (%s, %s, %s, %s)
"""


# ==========================================
# UPDATE CAMERA STATUS
# ==========================================

def cam_update_status(enable, camera_url, camera_name):

    cursor.execute(
        """
        UPDATE camera
        SET enable = %s
        WHERE CameraURL = %s
        AND CameraName = %s
        """,
        (enable, camera_url, camera_name)
    )

    print("Camera status updated")


# ==========================================
# AUTOMATICALLY CREATE / UPDATE CAMERAS
# ==========================================

def auto_enter_cam(name):

    # Find vendor
    cursor.execute(
        """
        SELECT VendorID, VendorName, NUMBER_CAM, URL, enable
        FROM vendor
        WHERE VendorName = %s
        """,
        (name,)
    )

    vendor = cursor.fetchone()

    if vendor is None:

        print("Vendor not found")
        return

    # --------------------------------------
    # Get vendor information
    # --------------------------------------

    vendor_id = vendor[0]
    cam_number = vendor[2]
    vendor_url = vendor[3]

    print("Vendor:", vendor[1])
    print("Number of cameras:", cam_number)
    print("Base URL:", vendor_url)

    # --------------------------------------
    # Generate base URL
    #
    # Example:
    #
    # .../stream/cam01
    #
    # becomes:
    #
    # .../stream/cam
    # --------------------------------------

    base_url = vendor_url[:-2]

    # --------------------------------------
    # Generate and test cameras
    # --------------------------------------

    for i in range(1, cam_number + 1):

        camera_name = f"CAM{i:02d}"

        camera_url = f"{base_url}{i:02d}"

        print()
        print("Testing:", camera_name)
        print("URL:", camera_url)

        # ----------------------------------
        # Check camera
        # ----------------------------------

        status = check_camera(camera_url)

        print("Status:", status)

        # ----------------------------------
        # Check if camera already exists
        # ----------------------------------

        cursor.execute(
            """
            SELECT CameraID
            FROM camera
            WHERE CameraURL = %s
            AND CameraName = %s
            """,
            (camera_url, camera_name)
        )

        camera = cursor.fetchone()

        # ----------------------------------
        # Camera already exists
        # ----------------------------------

        if camera is not None:

            cam_update_status(
                status,
                camera_url,
                camera_name
            )

        # ----------------------------------
        # Camera doesn't exist
        # ----------------------------------

        else:

            cursor.execute(
                camera_sql,
                (
                    camera_name,
                    vendor_id,
                    camera_url,
                    status
                )
            )

            print("Camera inserted")

    # --------------------------------------
    # Save changes
    # --------------------------------------

    conn.commit()

    print()
    print("All cameras processed successfully")


# ==========================================
# TEST
# ==========================================

auto_enter_cam("Vendor A")


# ==========================================
# SHOW CAMERAS
# ==========================================

cursor.execute("SELECT * FROM camera")

rows = cursor.fetchall()

print()
print("CAMERA DATABASE")
print("----------------")

for row in rows:
    print(row)


# ==========================================
# CLOSE DATABASE
# ==========================================

cursor.close()
conn.close()
