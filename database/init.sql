-- =========================================================
-- GUJARAT POLICE CCTV SYSTEM
-- DATABASE INITIALIZATION
-- =========================================================

CREATE DATABASE IF NOT EXISTS gujarat_police;

USE gujarat_police;


-- =========================================================
-- 1. STATE
-- =========================================================

CREATE TABLE IF NOT EXISTS state (
    StateID INT NOT NULL AUTO_INCREMENT,
    StateName VARCHAR(100) NOT NULL,
    StateCode VARCHAR(10) NOT NULL,
    enable BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (StateID),
    UNIQUE KEY uq_state_name (StateName),
    UNIQUE KEY uq_state_code (StateCode)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 2. DISTRICT
-- =========================================================

CREATE TABLE IF NOT EXISTS district (
    DistrictID INT NOT NULL AUTO_INCREMENT,
    StateID INT NOT NULL,
    DistrictName VARCHAR(100) NOT NULL,
    DistrictCode VARCHAR(20) DEFAULT NULL,
    enable BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (DistrictID),

    UNIQUE KEY uq_district_state_name (StateID, DistrictName),
    UNIQUE KEY uq_district_state_code (StateID, DistrictCode),

    KEY idx_district_state (StateID),

    CONSTRAINT fk_district_state
        FOREIGN KEY (StateID)
        REFERENCES state (StateID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 3. POLICE STATION
-- =========================================================

CREATE TABLE IF NOT EXISTS police_station (
    PoliceStationID INT NOT NULL AUTO_INCREMENT,
    DistrictID INT NOT NULL,
    StationName VARCHAR(150) NOT NULL,
    StationCode VARCHAR(30) DEFAULT NULL,
    enable BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (PoliceStationID),

    UNIQUE KEY uq_station_district_name
        (DistrictID, StationName),

    UNIQUE KEY uq_station_district_code
        (DistrictID, StationCode),

    KEY idx_station_district (DistrictID),

    CONSTRAINT fk_station_district
        FOREIGN KEY (DistrictID)
        REFERENCES district (DistrictID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 4. VENDOR
-- =========================================================

CREATE TABLE IF NOT EXISTS vendor (
    VendorID INT NOT NULL AUTO_INCREMENT,
    VendorName VARCHAR(255) NOT NULL,
    StateID INT NOT NULL,

    ContactName VARCHAR(255) DEFAULT NULL,
    ContactEmail VARCHAR(255) DEFAULT NULL,
    ContactPhone VARCHAR(50) DEFAULT NULL,
    APIEndpoint VARCHAR(2083) DEFAULT NULL,

    enable BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (VendorID),

    UNIQUE KEY uq_vendor_name_state
        (StateID, VendorName),

    KEY idx_vendor_state (StateID),

    CONSTRAINT fk_vendor_state
        FOREIGN KEY (StateID)
        REFERENCES state (StateID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 5. CAMERA
-- =========================================================

CREATE TABLE IF NOT EXISTS camera (
    CameraID INT NOT NULL AUTO_INCREMENT,

    CameraName VARCHAR(255) NOT NULL,

    PoliceStationID INT NOT NULL,
    VendorID INT NOT NULL,

    CameraType VARCHAR(50) DEFAULT NULL,
    Location VARCHAR(500) DEFAULT NULL,

    Latitude DECIMAL(10,7) DEFAULT NULL,
    Longitude DECIMAL(10,7) DEFAULT NULL,

    enable BOOLEAN NOT NULL DEFAULT TRUE,

    lifecycle_status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    retired_at TIMESTAMP NULL DEFAULT NULL,

    PRIMARY KEY (CameraID),

    KEY idx_camera_station (PoliceStationID),
    KEY idx_camera_vendor (VendorID),

    CONSTRAINT fk_camera_station
        FOREIGN KEY (PoliceStationID)
        REFERENCES police_station (PoliceStationID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_camera_vendor
        FOREIGN KEY (VendorID)
        REFERENCES vendor (VendorID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 6. CAMERA STREAM
-- =========================================================

CREATE TABLE IF NOT EXISTS camera_stream (
    StreamID INT NOT NULL AUTO_INCREMENT,

    CameraID INT NOT NULL,

    Protocol VARCHAR(30) NOT NULL,
    SourceURL VARCHAR(2083) NOT NULL,

    MediaMTXPath VARCHAR(500) DEFAULT NULL,

    Transport VARCHAR(30) DEFAULT NULL,

    enable BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (StreamID),

    KEY idx_stream_camera (CameraID),

    CONSTRAINT fk_stream_camera
        FOREIGN KEY (CameraID)
        REFERENCES camera (CameraID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 7. CAMERA RUNTIME STATUS
-- =========================================================

CREATE TABLE IF NOT EXISTS camera_runtime_status (
    CameraID INT NOT NULL,

    Status VARCHAR(30) NOT NULL DEFAULT 'OFFLINE',

    LastSeen DATETIME NULL,
    LastChecked DATETIME NULL,

    FailureReason VARCHAR(500) DEFAULT NULL,

    RetryCount INT NOT NULL DEFAULT 0,

    NextRetryAt DATETIME NULL,

    UpdatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (CameraID),

    CONSTRAINT fk_runtime_camera
        FOREIGN KEY (CameraID)
        REFERENCES camera (CameraID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 8. CAMERA STATUS HISTORY
-- =========================================================

CREATE TABLE IF NOT EXISTS camera_status_history (
    HistoryID BIGINT NOT NULL AUTO_INCREMENT,

    CameraID INT NOT NULL,

    OldStatus VARCHAR(30) DEFAULT NULL,
    NewStatus VARCHAR(30) NOT NULL,

    ChangedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    Reason VARCHAR(500) DEFAULT NULL,

    PRIMARY KEY (HistoryID),

    KEY idx_status_history_camera_time
        (CameraID, ChangedAt),

    CONSTRAINT fk_status_history_camera
        FOREIGN KEY (CameraID)
        REFERENCES camera (CameraID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 9. NETWORK COMMAND
-- =========================================================

CREATE TABLE IF NOT EXISTS network_command (
    CommandID BIGINT NOT NULL AUTO_INCREMENT,

    CameraID INT NOT NULL,

    CommandType VARCHAR(30) NOT NULL,

    CommandStatus VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    RequestedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    StartedAt DATETIME NULL,
    CompletedAt DATETIME NULL,

    RequestedBy VARCHAR(100) DEFAULT NULL,

    FailureReason VARCHAR(500) DEFAULT NULL,

    RetryCount INT NOT NULL DEFAULT 0,

    PRIMARY KEY (CommandID),

    KEY idx_command_camera_time
        (CameraID, RequestedAt),

    KEY idx_command_status
        (CommandStatus),

    CONSTRAINT fk_command_camera
        FOREIGN KEY (CameraID)
        REFERENCES camera (CameraID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 10. AI CONFIGURATION
-- =========================================================

CREATE TABLE IF NOT EXISTS ai_config (
    AIConfigID INT NOT NULL AUTO_INCREMENT,

    CameraID INT NOT NULL,

    VehicleDetection BOOLEAN NOT NULL DEFAULT FALSE,
    VehicleTracking BOOLEAN NOT NULL DEFAULT FALSE,
    VehicleCounting BOOLEAN NOT NULL DEFAULT FALSE,

    FaceDetection BOOLEAN NOT NULL DEFAULT FALSE,
    FaceRecognition BOOLEAN NOT NULL DEFAULT FALSE,

    HelmetDetection BOOLEAN NOT NULL DEFAULT FALSE,
    AccidentDetection BOOLEAN NOT NULL DEFAULT FALSE,

    ViolationDetection BOOLEAN NOT NULL DEFAULT FALSE,
    AnomalyDetection BOOLEAN NOT NULL DEFAULT FALSE,

    enable BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (AIConfigID),

    UNIQUE KEY uq_ai_config_camera (CameraID),

    CONSTRAINT fk_ai_config_camera
        FOREIGN KEY (CameraID)
        REFERENCES camera (CameraID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 11. AI EVENT
-- =========================================================

CREATE TABLE IF NOT EXISTS ai_event (
    EventID BIGINT NOT NULL AUTO_INCREMENT,

    CameraID INT NOT NULL,

    EventType VARCHAR(50) NOT NULL,

    EventTime DATETIME NOT NULL,

    ObjectType VARCHAR(50) DEFAULT NULL,

    ObjectCount INT DEFAULT NULL,

    Confidence DECIMAL(5,4) DEFAULT NULL,

    EvidenceURL VARCHAR(2083) DEFAULT NULL,

    Metadata JSON DEFAULT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (EventID),

    KEY idx_ai_event_camera_time
        (CameraID, EventTime),

    KEY idx_ai_event_type_time
        (EventType, EventTime),

    CONSTRAINT fk_ai_event_camera
        FOREIGN KEY (CameraID)
        REFERENCES camera (CameraID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4;