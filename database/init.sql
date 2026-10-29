CREATE DATABASE IF NOT EXISTS gujarat_police;

USE gujarat_police;


-- =========================================
-- STATE
-- =========================================

CREATE TABLE IF NOT EXISTS state (
    StateID INT NOT NULL AUTO_INCREMENT,
    StateName VARCHAR(100) NOT NULL,
    StateCode VARCHAR(10) DEFAULT NULL,
    enable BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (StateID),

    UNIQUE KEY uq_state_name (StateName),
    UNIQUE KEY uq_state_code (StateCode)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;


-- =========================================
-- VENDOR
-- =========================================

CREATE TABLE IF NOT EXISTS vendor (
    VendorID INT NOT NULL AUTO_INCREMENT,
    VendorName VARCHAR(255) NOT NULL,
    StateID INT NOT NULL,

    ContactName VARCHAR(255) DEFAULT NULL,
    ContactEmail VARCHAR(255) DEFAULT NULL,
    ContactPhone VARCHAR(50) DEFAULT NULL,

    URL VARCHAR(2083) DEFAULT NULL,

    enable BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (VendorID),

    KEY idx_vendor_state (StateID),

    CONSTRAINT fk_vendor_state
        FOREIGN KEY (StateID)
        REFERENCES state (StateID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;


-- =========================================
-- CAMERA
-- =========================================

CREATE TABLE IF NOT EXISTS camera (
    CameraID INT NOT NULL AUTO_INCREMENT,

    CameraName VARCHAR(255) NOT NULL,

    VendorID INT NOT NULL,

    CameraType VARCHAR(50) DEFAULT NULL,

    Location VARCHAR(500) DEFAULT NULL,

    Latitude DECIMAL(10,7) DEFAULT NULL,
    Longitude DECIMAL(10,7) DEFAULT NULL,

    enable BOOLEAN NOT NULL DEFAULT TRUE,
    statues VARCHAR (500) NOT NULL ,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (CameraID),

    KEY idx_camera_vendor (VendorID),

    CONSTRAINT fk_camera_vendor
        FOREIGN KEY (VendorID)
        REFERENCES vendor (VendorID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;