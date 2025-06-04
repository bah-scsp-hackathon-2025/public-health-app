# Alerts API Reference

## Overview
The Alerts API provides endpoints for managing security alerts within the system. All endpoints are prefixed with `/alerts` and tagged as "alerts".

## Base URL
```
/alerts
```

---

## Endpoints

### 1. Create Alert
**POST** `/alerts/`

Creates a new alert in the database.

#### Request Body
- **Content-Type**: `application/json`
- **Schema**: `AlertCreate`

```json
{
  "name": "string",
  "description": "string",
  "risk_score": "number",
  "risk_reason": "string",
  "location": "string",
  "latitude": "number",
  "longitude": "number"
}
```

#### Response
- **Status Code**: `201 Created`
- **Content-Type**: `application/json`
- **Schema**: `Alert` object

#### Error Responses
- **400 Bad Request**: Alert with the same name already exists
- **422 Unprocessable Entity**: Invalid request body

---

### 2. Get All Alerts
**GET** `/alerts/`

Retrieves a list of all alerts with default pagination.

#### Query Parameters
None explicitly defined, but the underlying function supports:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of records to skip for pagination |
| `limit` | integer | 100 | Maximum number of records to return |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: Array of `AlertResponse` objects

```json
[
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "risk_score": "number",
    "risk_reason": "string",
    "location": "string",
    "latitude": "number",
    "longitude": "number",
    "created": "string",
    "updated": "string"
  }
]
```

---

### 3. Get Alerts by Location/State
**GET** `/alerts/state/{location}`

Retrieves all alerts for a specific location or state.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | string | Yes | Location/state name (underscores will be converted to spaces) |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: Array of `AlertResponse` objects

#### Error Responses
- **404 Not Found**: No alerts found for the specified location

#### Notes
- Location matching is case-insensitive
- Underscores in the location parameter are automatically converted to spaces
- Example: `new_york` becomes `new york` for matching

---

### 4. Get Alert by ID
**GET** `/alerts/{alert_id}`

Retrieves a specific alert by its ID.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `alert_id` | string | Yes | Unique identifier for the alert |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: `AlertResponse` object

#### Error Responses
- **404 Not Found**: Alert not found

---

### 5. Update Alert
**PUT** `/alerts/{alert_id}`

Updates an existing alert with new information.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `alert_id` | string | Yes | Unique identifier for the alert |

#### Request Body
- **Content-Type**: `application/json`
- **Schema**: `AlertUpdate`

```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "risk_score": "number (optional)",
  "risk_reason": "string (optional)",
  "location": "string (optional)",
  "latitude": "number (optional)",
  "longitude": "number (optional)"
}
```

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: `AlertResponse` object

#### Error Responses
- **404 Not Found**: Alert not found
- **422 Unprocessable Entity**: Invalid request body

#### Notes
- Only provided fields will be updated
- The `updated` timestamp is automatically set to the current time
- All fields are optional in the update request

---

### 6. Delete Alert
**DELETE** `/alerts/{alert_id}`

Deletes a specific alert from the database.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `alert_id` | string | Yes | Unique identifier for the alert |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: `AlertResponse` object (deleted alert data)

#### Error Responses
- **404 Not Found**: Alert not found

---

## Data Models

### AlertCreate
```json
{
  "name": "string",
  "description": "string",
  "risk_score": "number",
  "risk_reason": "string",
  "location": "string",
  "latitude": "number",
  "longitude": "number"
}
```

### AlertUpdate
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "risk_score": "number (optional)",
  "risk_reason": "string (optional)",
  "location": "string (optional)",
  "latitude": "number (optional)",
  "longitude": "number (optional)"
}
```

### AlertResponse
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "risk_score": "number",
  "risk_reason": "string",
  "location": "string",
  "latitude": "number",
  "longitude": "number",
  "created": "string (YYYY-MM-DD HH:MM:SS)",
  "updated": "string (YYYY-MM-DD HH:MM:SS)"
}
```

---

## Usage Examples

### Create a New Alert
```bash
curl -X POST "/alerts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Risk Security Alert",
    "description": "Suspicious activity detected in server room",
    "risk_score": 8.5,
    "risk_reason": "Unauthorized access attempt",
    "location": "New York",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

### Get All Alerts
```bash
curl -X GET "/alerts/"
```

### Get Alerts by Location
```bash
curl -X GET "/alerts/state/new_york"
```

### Get Specific Alert
```bash
curl -X GET "/alerts/alert-123"
```

### Update an Alert
```bash
curl -X PUT "/alerts/alert-123" \
  -H "Content-Type: application/json" \
  -d '{
    "risk_score": 9.0,
    "description": "Updated: Critical security breach detected"
  }'
```

### Delete an Alert
```bash
curl -X DELETE "/alerts/alert-123"
```

---

## Field Descriptions

### Alert Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Auto-generated unique identifier |
| `name` | string | Alert name/title (must be unique) |
| `description` | string | Detailed description of the alert |
| `risk_score` | number | Numerical risk assessment score |
| `risk_reason` | string | Explanation of why this risk score was assigned |
| `location` | string | Geographic location where alert originated |
| `latitude` | number | Geographic latitude coordinate |
| `longitude` | number | Geographic longitude coordinate |
| `created` | string | Timestamp when alert was created |
| `updated` | string | Timestamp when alert was last modified |


# Policies API Reference

## Overview
The Policies API provides endpoints for managing policies within the system. All endpoints are prefixed with `/policies` and tagged as "policies".

## Base URL
```
/policies
```

---

## Endpoints

### 1. Create Policy
**POST** `/policies/`

Creates a new policy in the database.

#### Request Body
- **Content-Type**: `application/json`
- **Schema**: `PolicyCreate`

```json
{
  "title": "string",
  "content": "string",
  "author": "string",
  "approved": "boolean",
  "alert_id": "string",
  "strategy_id": "string"
}
```

#### Response
- **Status Code**: `201 Created`
- **Content-Type**: `application/json`
- **Schema**: `Policy` object

#### Error Responses
- **400 Bad Request**: Policy with the same title already exists
- **422 Unprocessable Entity**: Invalid request body

---

### 2. Get All Policies
**GET** `/policies/`

Retrieves a paginated list of all policies.

#### Query Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of records to skip for pagination |
| `limit` | integer | 100 | Maximum number of records to return |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: Array of `PolicyResponse` objects

```json
[
  {
    "id": "string",
    "title": "string",
    "content": "string",
    "author": "string",
    "approved": "boolean",
    "created": "string",
    "updated": "string",
    "alert_id": "string",
    "strategy_id": "string"
  }
]
```

---

### 3. Get Policy by ID
**GET** `/policies/{policy_id}`

Retrieves a specific policy by its ID.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `policy_id` | string | Yes | Unique identifier for the policy |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: `PolicyResponse` object

#### Error Responses
- **404 Not Found**: Policy not found

---

### 4. Update Policy
**PUT** `/policies/{policy_id}`

Updates an existing policy with new information.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `policy_id` | string | Yes | Unique identifier for the policy |

#### Request Body
- **Content-Type**: `application/json`
- **Schema**: `PolicyUpdate`

```json
{
  "title": "string (optional)",
  "content": "string (optional)",
  "author": "string (optional)",
  "approved": "boolean (optional)",
  "alert_id": "string (optional)",
  "strategy_id": "string (optional)"
}
```

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: `PolicyResponse` object

#### Error Responses
- **404 Not Found**: Policy not found
- **422 Unprocessable Entity**: Invalid request body

---

### 5. Delete Policy
**DELETE** `/policies/{policy_id}`

Deletes a specific policy from the database.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `policy_id` | string | Yes | Unique identifier for the policy |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: `PolicyResponse` object (deleted policy data)

#### Error Responses
- **404 Not Found**: Policy not found

---

### 6. Generate Policy from Strategy
**GET** `/policies/generate/{strategy_id}`

Generates a new policy based on an existing strategy.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `strategy_id` | string | Yes | Unique identifier for the strategy |

#### Response
- **Status Code**: `201 Created`
- **Content-Type**: `application/json`
- **Schema**: `Policy` object

#### Error Responses
- **404 Not Found**: Strategy not found

#### Notes
- Currently uses dummy data with hardcoded values
- Author is set to "bri"
- Alert ID is set to "1"
- Approved status is set to `false`
- Strategy ID is set to "2"

---

### 7. Get Policies by Status and Alert
**GET** `/policies/{status_}/alert/{alert_id}`

Retrieves policies filtered by approval status and alert ID.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status_` | string | Yes | Policy status ("approved" or any other value for unapproved) |
| `alert_id` | string | Yes | Alert identifier |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: Array of `PolicyResponse` objects

#### Error Responses
- **404 Not Found**: No policies found matching criteria

---

### 8. Get Policies by Alert
**GET** `/policies/alert/{alert_id}`

Retrieves all policies associated with a specific alert.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `alert_id` | string | Yes | Alert identifier |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: Array of `PolicyResponse` objects

#### Error Responses
- **404 Not Found**: No policies found for the specified alert

---

### 9. Get Policies by Status
**GET** `/policies/{status_}/`

Retrieves policies filtered by approval status.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status_` | string | Yes | Policy status ("approved" or any other value for unapproved) |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: Array of `PolicyResponse` objects

#### Error Responses
- **404 Not Found**: No policies found matching the specified status

---

## Data Models

### PolicyCreate
```json
{
  "title": "string",
  "content": "string",
  "author": "string",
  "approved": "boolean",
  "alert_id": "string",
  "strategy_id": "string"
}
```

### PolicyUpdate
```json
{
  "title": "string (optional)",
  "content": "string (optional)",
  "author": "string (optional)",
  "approved": "boolean (optional)",
  "alert_id": "string (optional)",
  "strategy_id": "string (optional)"
}
```

### PolicyResponse
```json
{
  "id": "string",
  "title": "string",
  "content": "string",
  "author": "string",
  "approved": "boolean",
  "created": "string (YYYY-MM-DD HH:MM:SS)",
  "updated": "string (YYYY-MM-DD HH:MM:SS)",
  "alert_id": "string",
  "strategy_id": "string"
}
```

---

## Usage Examples

### Create a New Policy
```bash
curl -X POST "/policies/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Security Policy",
    "content": "This policy outlines security procedures...",
    "author": "admin",
    "approved": false,
    "alert_id": "alert-123",
    "strategy_id": "strategy-456"
  }'
```

### Get All Policies with Pagination
```bash
curl -X GET "/policies/?skip=0&limit=10"
```

### Update a Policy
```bash
curl -X PUT "/policies/policy-123" \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "content": "Updated policy content..."
  }'
```

### Get Approved Policies for an Alert
```bash
curl -X GET "/policies/approved/alert/alert-123"
```

# Strategies API Reference

## Overview
The Strategies API provides endpoints for managing response strategies associated with security alerts. All endpoints are prefixed with `/strategies` and tagged as "strategies".

## Base URL
```
/strategies
```

---

## Endpoints

### 1. Generate Strategies for Alert
**GET** `/strategies/generate/{alert_id}`

Generates multiple strategies based on an existing alert. Currently creates 3 strategies with dummy data.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `alert_id` | string | Yes | Unique identifier for the alert |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: Array of `StrategyResponse` objects

```json
[
  {
    "id": "string",
    "short_description": "string",
    "full_description": "string",
    "alert_id": "string"
  }
]
```

#### Error Responses
- **404 Not Found**: Alert not found

#### Notes
- Currently generates 3 strategies with placeholder logic
- Strategy names are created by appending " 1", " 2", " 3" to the alert name
- Full descriptions are copied from the source alert description
- All generated strategies are automatically saved to the database

---

### 2. Get Strategy by ID
**GET** `/strategies/{strategy_id}`

Retrieves a specific strategy by its ID.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `strategy_id` | string | Yes | Unique identifier for the strategy |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: `StrategyResponse` object

```json
{
  "id": "string",
  "short_description": "string",
  "full_description": "string",
  "alert_id": "string"
}
```

#### Error Responses
- **404 Not Found**: Strategy not found

---

### 3. Get Strategies by Alert
**GET** `/strategies/alert/{alert_id}`

Retrieves all strategies associated with a specific alert.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `alert_id` | string | Yes | Unique identifier for the alert |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: Array of `StrategyResponse` objects

#### Error Responses
- **404 Not Found**: No strategies found for the specified alert

---

### 4. Create Strategy
**POST** `/strategies/`

Creates a new strategy in the database.

#### Request Body
- **Content-Type**: `application/json`
- **Schema**: `StrategyCreate`

```json
{
  "short_description": "string",
  "full_description": "string",
  "alert_id": "string"
}
```

#### Response
- **Status Code**: `201 Created`
- **Content-Type**: `application/json`
- **Schema**: `Strategy` object

#### Error Responses
- **422 Unprocessable Entity**: Invalid request body

---

### 5. Update Strategy
**PUT** `/strategies/{strategy_id}`

Updates an existing strategy with new information.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `strategy_id` | string | Yes | Unique identifier for the strategy |

#### Request Body
- **Content-Type**: `application/json`
- **Schema**: `StrategyUpdate`

```json
{
  "short_description": "string (optional)",
  "full_description": "string (optional)"
}
```

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: `StrategyResponse` object

#### Error Responses
- **404 Not Found**: Strategy not found
- **422 Unprocessable Entity**: Invalid request body

#### Notes
- Only provided fields will be updated
- The `alert_id` cannot be modified through this endpoint

---

### 6. Delete Strategy
**DELETE** `/strategies/{strategy_id}`

Deletes a specific strategy from the database.

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `strategy_id` | string | Yes | Unique identifier for the strategy |

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: `StrategyResponse` object (deleted strategy data)

#### Error Responses
- **404 Not Found**: Strategy not found

---

## Data Models

### StrategyCreate
```json
{
  "short_description": "string",
  "full_description": "string",
  "alert_id": "string"
}
```

### StrategyUpdate
```json
{
  "short_description": "string (optional)",
  "full_description": "string (optional)"
}
```

### StrategyResponse
```json
{
  "id": "string",
  "short_description": "string",
  "full_description": "string",
  "alert_id": "string"
}
```

---

## Usage Examples

### Generate Strategies for an Alert
```bash
curl -X GET "/strategies/generate/alert-123"
```

### Create a New Strategy
```bash
curl -X POST "/strategies/" \
  -H "Content-Type: application/json" \
  -d '{
    "short_description": "Immediate Response Protocol",
    "full_description": "This strategy outlines the immediate steps to take when a security breach is detected...",
    "alert_id": "alert-123"
  }'
```

### Get a Specific Strategy
```bash
curl -X GET "/strategies/strategy-456"
```

### Get All Strategies for an Alert
```bash
curl -X GET "/strategies/alert/alert-123"
```

### Update a Strategy
```bash
curl -X PUT "/strategies/strategy-456" \
  -H "Content-Type: application/json" \
  -d '{
    "short_description": "Updated Response Protocol",
    "full_description": "This updated strategy includes new procedures for handling security incidents..."
  }'
```

### Delete a Strategy
```bash
curl -X DELETE "/strategies/strategy-456"
```

---

## Field Descriptions

### Strategy Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Auto-generated unique identifier |
| `short_description` | string | Brief summary or title of the strategy |
| `full_description` | string | Detailed description of the strategy and its implementation |
| `alert_id` | string | Reference to the associated alert |


# Summary API Reference

## Overview
The Summary API provides endpoints for retrieving system summary information. All endpoints are prefixed with `/summary` and tagged as "summary".

## Base URL
```
/summary
```

---

## Endpoints

### 1. Get System Summary
**GET** `/summary/`

Retrieves a comprehensive summary of the current system state, including information about alerts and other system components.

#### Query Parameters
None

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: `SummaryResponse` object

```json
{
  "description": "string"
}
```

---

## Data Models

### SummaryResponse
```json
{
  "description": "string"
}
```

---

## Usage Examples

### Get System Summary
```bash
curl -X GET "/summary/"
```

### Example Response
```json
{
  "description": "High Risk Security Alert; Network Intrusion Alert; Physical Access Breach"
}
```

---


## Field Descriptions

### Summary Fields

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Textual summary of the current system state |


# Trends API Reference

## Overview
The Trends API provides endpoints for retrieving trend analysis data. All endpoints are prefixed with `/trends` and tagged as "trends".

## Base URL
```
/trends
```

---

## Endpoints

### 1. Get Trends
**GET** `/trends/`

Retrieves trend analysis data for the system.

#### Query Parameters
None

#### Response
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Schema**: Array of `TrendResponse` objects

```json
[
  {
    "set1": [1, 2, 3, 4]
  }
]
```

---

## Data Models

### TrendResponse
```json
{}
```
