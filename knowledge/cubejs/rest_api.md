# Cube.js REST API

Cube.js provides a powerful REST API that allows you to query your data models and retrieve business intelligence data. This document covers the key endpoints and query formats used by the Golett agents.

## Base URL

The Cube.js REST API is typically available at:

```
http://your-cubejs-server/cubejs-api/v1
```

## Authentication

Most Cube.js deployments require authentication using an API token:

```
Authorization: Bearer YOUR_API_TOKEN
```

## Key Endpoints

### 1. /load

This is the primary endpoint for querying data. It accepts POST requests with a JSON body containing the query specification.

**Example Request:**
```json
{
  "query": {
    "measures": ["Orders.count"],
    "timeDimensions": [
      {
        "dimension": "Orders.createdAt",
        "granularity": "month",
        "dateRange": ["2022-01-01", "2022-12-31"]
      }
    ],
    "dimensions": ["Orders.status"]
  }
}
```

**Example Response:**
```json
{
  "data": [
    {
      "Orders.createdAt": "2022-01-01T00:00:00.000",
      "Orders.status": "completed",
      "Orders.count": 321
    },
    {
      "Orders.createdAt": "2022-01-01T00:00:00.000",
      "Orders.status": "processing",
      "Orders.count": 123
    }
  ]
}
```

### 2. /meta

This endpoint returns metadata about available cubes, measures, dimensions, and segments.

**Example Response:**
```json
{
  "cubes": [
    {
      "name": "Orders",
      "title": "Orders",
      "measures": [
        {
          "name": "Orders.count",
          "title": "Orders Count",
          "type": "number"
        },
        {
          "name": "Orders.totalAmount",
          "title": "Orders Total Amount",
          "type": "number"
        }
      ],
      "dimensions": [
        {
          "name": "Orders.status",
          "title": "Orders Status",
          "type": "string"
        },
        {
          "name": "Orders.createdAt",
          "title": "Orders Created At",
          "type": "time"
        }
      ]
    }
  ]
}
```

### 3. /sql

This endpoint executes SQL queries directly. Note that this is only available if enabled by the Cube.js configuration.

**Example Request:**
```json
{
  "query": "SELECT * FROM orders LIMIT 10"
}
```

### 4. /dry-run

This endpoint returns the SQL that would be generated for a query without executing it.

**Example Request:**
```json
{
  "query": {
    "measures": ["Orders.count"],
    "dimensions": ["Orders.status"]
  }
}
```

**Example Response:**
```json
{
  "sql": {
    "sql": "SELECT `orders`.`status` AS `orders__status`, count(*) AS `orders__count` FROM `orders` AS `orders` GROUP BY 1",
    "timeDimensions": [],
    "rawQuery": false,
    "external": false,
    "dialect": "mysql"
  }
}
```

## Query Format

The Cube.js query format is a JSON object that defines what data you want to retrieve.

### Key Components:

1. **Measures**: The metrics you want to calculate.
   ```json
   "measures": ["Orders.count", "Orders.totalAmount"]
   ```

2. **Dimensions**: The attributes you want to group by.
   ```json
   "dimensions": ["Orders.status", "Users.country"]
   ```

3. **Time Dimensions**: Special handling for time-based dimensions.
   ```json
   "timeDimensions": [
     {
       "dimension": "Orders.createdAt",
       "granularity": "month",  // year, quarter, month, week, day, hour, minute, second
       "dateRange": ["2022-01-01", "2022-12-31"]
     }
   ]
   ```

4. **Filters**: Conditions to filter the data.
   ```json
   "filters": [
     {
       "member": "Orders.status",
       "operator": "equals",
       "values": ["completed"]
     }
   ]
   ```

5. **Limit**: Maximum number of rows to return.
   ```json
   "limit": 1000
   ```

6. **Offset**: Number of rows to skip.
   ```json
   "offset": 0
   ```

7. **Order**: Sorting specifications.
   ```json
   "order": [
     {
       "id": "Orders.count",
       "desc": true
     }
   ]
   ```

## Common Filter Operators

Cube.js supports various filter operators:

1. **equals**: Exact match.
   ```json
   {
     "member": "Orders.status",
     "operator": "equals",
     "values": ["completed"]
   }
   ```

2. **notEquals**: Not equal to.
   ```json
   {
     "member": "Orders.status",
     "operator": "notEquals",
     "values": ["cancelled"]
   }
   ```

3. **contains**: String contains.
   ```json
   {
     "member": "Orders.comment",
     "operator": "contains",
     "values": ["special"]
   }
   ```

4. **gt/gte**: Greater than / Greater than or equal to.
   ```json
   {
     "member": "Orders.totalAmount",
     "operator": "gt",
     "values": ["100"]
   }
   ```

5. **lt/lte**: Less than / Less than or equal to.
   ```json
   {
     "member": "Orders.totalAmount",
     "operator": "lt",
     "values": ["1000"]
   }
   ```

6. **inDateRange**: Filter time dimensions.
   ```json
   {
     "member": "Orders.createdAt",
     "operator": "inDateRange",
     "values": ["2022-01-01", "2022-12-31"]
   }
   ```

7. **set/notSet**: Check if value is not NULL / is NULL.
   ```json
   {
     "member": "Orders.comment",
     "operator": "set"
   }
   ```

## Logical Operators

You can use logical operators for complex filtering:

```json
"filters": [
  {
    "or": [
      {
        "member": "Orders.status",
        "operator": "equals",
        "values": ["completed"]
      },
      {
        "and": [
          {
            "member": "Orders.status",
            "operator": "equals",
            "values": ["processing"]
          },
          {
            "member": "Orders.totalAmount",
            "operator": "gt",
            "values": ["100"]
          }
        ]
      }
    ]
  }
]
```

## Error Handling

The API returns error responses with HTTP status codes and JSON bodies containing error details:

```json
{
  "error": "Error message"
}
```

Common status codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 500: Internal Server Error 