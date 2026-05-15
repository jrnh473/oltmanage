-- OLT Management System Database Schema
-- MariaDB 10.x compatible

-- 1. OLT Devices Table
CREATE TABLE IF NOT EXISTS olt_devices (
    id VARCHAR(36) PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    vendor VARCHAR(50) NOT NULL,
    ip_address VARCHAR(50) NOT NULL,
    snmp_port INT DEFAULT 161,
    ssh_port INT DEFAULT 22,
    snmp_community VARCHAR(255),
    username VARCHAR(100),
    password VARCHAR(255),
    connection_method ENUM('SNMP', 'SSH', 'TELNET') DEFAULT 'SNMP',
    status ENUM('ONLINE', 'OFFLINE', 'ERROR', 'UNKNOWN') DEFAULT 'UNKNOWN',
    cpu_usage FLOAT DEFAULT 0.0,
    memory_usage FLOAT DEFAULT 0.0,
    temperature FLOAT DEFAULT 0.0,
    uptime_seconds INT DEFAULT 0,
    firmware_version VARCHAR(100),
    serial_number VARCHAR(100),
    total_onu_count INT DEFAULT 0,
    online_onu_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_check_at TIMESTAMP NULL,
    UNIQUE KEY unique_ip_port (ip_address, snmp_port),
    INDEX idx_vendor (vendor),
    INDEX idx_status (status),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. ONUs (Optical Network Units) Table
CREATE TABLE IF NOT EXISTS onus (
    id VARCHAR(100) PRIMARY KEY,
    device_id VARCHAR(36) NOT NULL,
    port_id INT NOT NULL,
    onu_index INT NOT NULL,
    serial_number VARCHAR(100),
    mac_address VARCHAR(20),
    ip_address VARCHAR(50),
    status ENUM('ONLINE', 'OFFLINE', 'ERROR') DEFAULT 'OFFLINE',
    vendor_name VARCHAR(100),
    hardware_version VARCHAR(100),
    software_version VARCHAR(100),
    optical_power_downstream FLOAT,
    optical_power_upstream FLOAT,
    distance_km FLOAT,
    vlan_id INT,
    bandwidth_upstream INT,
    bandwidth_downstream INT,
    description VARCHAR(255),
    last_state_change TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES olt_devices(id) ON DELETE CASCADE,
    INDEX idx_device_port (device_id, port_id),
    INDEX idx_status (status),
    INDEX idx_serial (serial_number),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. PON Ports Table
CREATE TABLE IF NOT EXISTS pon_ports (
    id VARCHAR(100) PRIMARY KEY,
    device_id VARCHAR(36) NOT NULL,
    port_number INT NOT NULL,
    port_name VARCHAR(100),
    status ENUM('UP', 'DOWN', 'ERROR') DEFAULT 'DOWN',
    optical_power_downstream FLOAT,
    optical_power_upstream FLOAT,
    wavelength VARCHAR(50),
    onu_count INT DEFAULT 0,
    enabled BOOLEAN DEFAULT TRUE,
    admin_status ENUM('UP', 'DOWN') DEFAULT 'UP',
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES olt_devices(id) ON DELETE CASCADE,
    UNIQUE KEY unique_device_port (device_id, port_number),
    INDEX idx_device (device_id),
    INDEX idx_status (status),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Ethernet Ports Table
CREATE TABLE IF NOT EXISTS ethernet_ports (
    id VARCHAR(100) PRIMARY KEY,
    device_id VARCHAR(36) NOT NULL,
    port_number INT NOT NULL,
    port_name VARCHAR(100),
    status ENUM('UP', 'DOWN', 'ERROR') DEFAULT 'DOWN',
    speed VARCHAR(20),
    duplex ENUM('FULL', 'HALF') DEFAULT 'FULL',
    mtu INT DEFAULT 1500,
    vlan_id INT,
    enabled BOOLEAN DEFAULT TRUE,
    admin_status ENUM('UP', 'DOWN') DEFAULT 'UP',
    rx_packets BIGINT DEFAULT 0,
    tx_packets BIGINT DEFAULT 0,
    rx_bytes BIGINT DEFAULT 0,
    tx_bytes BIGINT DEFAULT 0,
    rx_errors BIGINT DEFAULT 0,
    tx_errors BIGINT DEFAULT 0,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES olt_devices(id) ON DELETE CASCADE,
    UNIQUE KEY unique_device_port (device_id, port_number),
    INDEX idx_device (device_id),
    INDEX idx_status (status),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Device Metrics History Table
CREATE TABLE IF NOT EXISTS device_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(36) NOT NULL,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    temperature FLOAT,
    online_onu_count INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES olt_devices(id) ON DELETE CASCADE,
    INDEX idx_device_timestamp (device_id, timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Device Logs Table
CREATE TABLE IF NOT EXISTS device_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(36) NOT NULL,
    log_type ENUM('INFO', 'WARNING', 'ERROR', 'DEBUG') DEFAULT 'INFO',
    message TEXT,
    operation VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES olt_devices(id) ON DELETE CASCADE,
    INDEX idx_device_type (device_id, log_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
