# Target App Architecture (Draft)

## 1. Overview

The **Target App** represents the vulnerable Windows system that communicates with the **Attacker App (Raspberry Pi)**. It receives scanning requests, returns simulated vulnerabilities, manages sessions, and displays attack progress to the user.

The architecture is divided into:

* **Frontend (UI/UX):** Already completed by another team.
* **Backend Logic:** Implemented in **C++**.
* **Communication Layer:** REST-like API using standard JSON.
* **Local Database:** To store sessions, history, logs, and attack results.

---

## 2. System Architecture

### **2.1 Components**

* **QML UI**

  * Agent Dashboard
  * Connection Page
  * Scan Page
  * History Page
  * Log Page
  * Settings Page

* **C++ Backend Modules**

  * Session Manager
  * API Client (HTTP/Socket)
  * Input Validator
  * Attack Progress Manager
  * Data Parser (JSON Processor)
  * DB Manager (SQLite)

* **Database Layer (SQLite)**

  * Sessions Table
  * Scan Results Table
  * Attack History Table
  * Logs Table

* **Communication Layer**

  * Handles Target ID authentication
  * Sends/receives JSON data
  * Manages responses from Attacker App

---

## 3. API Communication Flow

### **3.1 Flow Summary**

1. Target App generates or receives a **Target ID**.
2. User enters Attacker App ID → Backend validates it.
3. Target App establishes communication with Raspberry Pi.
4. Requests like **scan**, **enumeration**, **attack simulation** are sent.
5. Raspberry Pi (Attacker App) responds with JSON containing:

   * Scan results
   * Open ports
   * Vulnerabilities
   * Attack phases
6. Target App displays results & stores them locally.

### **3.2 JSON Format (Standard)**

Examples:

#### **Request**

```json
{
  "target_id": "TGT-8822",
  "session_id": "S-1221",
  "request": "start_scan"
}
```

#### **Response**

```json
{
  "status": "success",
  "open_ports": [22, 80, 443],
  "vulnerabilities": [
    {"id": "CVE-2022-122", "risk": "high"}
  ]
}
```

---

## 4. Security Requirements

### **4.1 Authentication**

* All communication requires a valid **Target ID**.
* Session token must be validated for each request.

### **4.2 Input Validation (C++)**

Validate:

* Target ID format
* Attacker ID format
* API responses
* JSON fields (must match expected structure)

Reject:

* Empty fields
* Malformed JSON
* Invalid session tokens

### **4.3 Device Authorization**

Target App must accept messages **only** from the connected Attacker App.

### **4.4 Error Handling**

* Invalid API response → log + reject
* Connection lost → display notification
* Session expired → regenerate session

---

## 5. Database Architecture

### **5.1 SQLite Tables**

#### **Sessions**

| Field       | Type     |
| ----------- | -------- |
| session_id  | TEXT     |
| target_id   | TEXT     |
| attacker_id | TEXT     |
| timestamp   | DATETIME |

#### **ScanResults**

| Field           | Type        |
| --------------- | ----------- |
| scan_id         | TEXT        |
| session_id      | TEXT        |
| open_ports      | TEXT (JSON) |
| vulnerabilities | TEXT (JSON) |

#### **AttackHistory**

| Field      | Type        |
| ---------- | ----------- |
| history_id | TEXT        |
| session_id | TEXT        |
| result     | TEXT (JSON) |

#### **Logs**

| Field     | Type     |
| --------- | -------- |
| log_id    | INTEGER  |
| timestamp | DATETIME |
| message   | TEXT     |

---

## 6. Target App Backend Responsibilities

### **Connection Page**

* Validate Attacker ID.
* Create a communication session.
* Store session in DB.

### **Scan Page**

* Send scan request.
* Receive ports, vulnerabilities.
* Display results.
* Save scan in DB.

### **History Page**

* List all past attacks.
* Load selected history.

### **Log Page**

* Real-time logging of all communication.

### **Settings Page**

* Regenerate Target ID.
* Reset session.
* Configure network settings.

---

## 7. Communication Flow Diagram (Simplified)

```
[Target App UI]
       |
       v
  [C++ Backend]
       |
       v
[API Client] --- JSON ---> [Attacker App]
       ^                       |
       |------ JSON <-----------
```

---

## 8. Summary

This architecture ensures:

* Clean separation between UI and logic
* Secure communication
* Scalable database structure
* Modular components for easy team collaboration

You can now start implementing:

* DB schema
* API client class
* Input validation functions
* Communication flow handler
