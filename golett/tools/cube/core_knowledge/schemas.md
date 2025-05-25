# Cube.js Data Modeling and Schemas

Cube.js uses a data modeling layer that defines your business metrics, relations between tables, and query logic. This document covers the key concepts and syntax for Cube.js schemas.

## Schema File Structure

Cube.js schemas can be defined in YAML or JavaScript files. For YAML, the file structure looks like:

```yaml
# orders.yml
cubes:
  - name: Orders
    sql_table: orders
    
    joins:
      - name: Users
        relationship: many_to_one
        sql: "{CUBE}.user_id = {Users}.id"
    
    measures:
      - name: count
        type: count
      
      - name: total_amount
        sql: amount
        type: sum
    
    dimensions:
      - name: status
        sql: status
        type: string
      
      - name: created_at
        sql: created_at
        type: time
```

## Key Components

### 1. Cubes

Cubes are the building blocks of your data model. They typically represent a database table or a view.

```yaml
cubes:
  - name: Orders
    sql_table: orders  # or sql: SELECT * FROM orders
    description: "Orders information"
```

### 2. Measures

Measures are the metrics you want to calculate:

```yaml
measures:
  - name: count
    type: count
    description: "Total number of orders"
  
  - name: total_amount
    sql: amount
    type: sum
    format: currency
    description: "Sum of order amounts"
    
  - name: average_amount
    sql: amount
    type: avg
    format: currency
    description: "Average order amount"
```

Common measure types:
- `count` - Counts records
- `sum` - Sums the specified field values
- `avg` - Calculates the average of field values
- `min` - Returns the minimum value
- `max` - Returns the maximum value
- `count_distinct` - Counts unique values

### 3. Dimensions

Dimensions are attributes you can filter or group by:

```yaml
dimensions:
  - name: id
    sql: id
    type: number
    primary_key: true
    
  - name: status
    sql: status
    type: string
    
  - name: created_at
    sql: created_at
    type: time
```

Common dimension types:
- `string` - Text values
- `number` - Numeric values
- `boolean` - True/false values
- `time` - Dates and times
- `geo` - Geographic data

### 4. Joins

Joins define relationships between cubes:

```yaml
joins:
  - name: Users
    relationship: many_to_one
    sql: "{CUBE}.user_id = {Users}.id"
```

Relationship types:
- `one_to_one`
- `one_to_many`
- `many_to_one`
- `many_to_many`

### 5. Pre-aggregations

Pre-aggregations are materialized query results stored as tables:

```yaml
pre_aggregations:
  - name: monthly_orders
    measures:
      - count
      - total_amount
    dimensions:
      - status
    time_dimension: created_at
    granularity: month
```

## Advanced Features

### 1. Calculated Fields

You can define calculated measures and dimensions:

```yaml
measures:
  - name: revenue
    sql: amount
    type: sum
    
  - name: cost
    sql: cost_per_item * quantity
    type: sum
    
  - name: profit
    sql: "{CUBE}.revenue - {CUBE}.cost"
    type: number
```

### 2. Filters

You can add filters to cubes or measures:

```yaml
measures:
  - name: completed_count
    type: count
    filters:
      - sql: "{CUBE}.status = 'completed'"
```

### 3. Segments

Segments are predefined filters that can be reused:

```yaml
segments:
  - name: completed
    sql: "{CUBE}.status = 'completed'"
    
  - name: processing
    sql: "{CUBE}.status = 'processing'"
```

### 4. Drill Downs

Drill downs define hierarchical relationships:

```yaml
dimensions:
  - name: country
    sql: country
    type: string
    drill_members:
      - city
      - postal_code
  
  - name: city
    sql: city
    type: string
    
  - name: postal_code
    sql: postal_code
    type: string
```

## Example Schemas

### 1. Basic E-commerce Schema

```yaml
# orders.yml
cubes:
  - name: Orders
    sql_table: orders
    
    joins:
      - name: Users
        relationship: many_to_one
        sql: "{CUBE}.user_id = {Users}.id"
      
      - name: Products
        relationship: many_to_one
        sql: "{CUBE}.product_id = {Products}.id"
    
    measures:
      - name: count
        type: count
        description: "Number of orders"
      
      - name: total_amount
        sql: amount
        type: sum
        description: "Total order amounts"
    
    dimensions:
      - name: id
        sql: id
        type: number
        primary_key: true
      
      - name: status
        sql: status
        type: string
      
      - name: created_at
        sql: created_at
        type: time
    
    segments:
      - name: completed
        sql: "{CUBE}.status = 'completed'"
      
      - name: processing
        sql: "{CUBE}.status = 'processing'"
    
    pre_aggregations:
      - name: monthly
        measures:
          - count
          - total_amount
        dimensions:
          - status
        time_dimension: created_at
        granularity: month
```

```yaml
# users.yml
cubes:
  - name: Users
    sql_table: users
    
    measures:
      - name: count
        type: count
    
    dimensions:
      - name: id
        sql: id
        type: number
        primary_key: true
      
      - name: name
        sql: name
        type: string
      
      - name: email
        sql: email
        type: string
      
      - name: country
        sql: country
        type: string
        drill_members:
          - city
      
      - name: city
        sql: city
        type: string
      
      - name: created_at
        sql: created_at
        type: time
```

### 2. Financial Analytics Schema

```yaml
# transactions.yml
cubes:
  - name: Transactions
    sql_table: transactions
    
    joins:
      - name: Accounts
        relationship: many_to_one
        sql: "{CUBE}.account_id = {Accounts}.id"
      
      - name: Categories
        relationship: many_to_one
        sql: "{CUBE}.category_id = {Categories}.id"
    
    measures:
      - name: count
        type: count
      
      - name: total_amount
        sql: amount
        type: sum
        format: currency
      
      - name: average_amount
        sql: amount
        type: avg
        format: currency
    
    dimensions:
      - name: id
        sql: id
        type: number
        primary_key: true
      
      - name: type
        sql: type
        type: string
      
      - name: description
        sql: description
        type: string
      
      - name: date
        sql: date
        type: time
    
    segments:
      - name: income
        sql: "{CUBE}.type = 'income'"
      
      - name: expense
        sql: "{CUBE}.type = 'expense'"
```

## Best Practices

1. **Use Clear Naming**: Use descriptive names for cubes, measures, and dimensions.

2. **Add Descriptions**: Document your schema with descriptions for all components.

3. **Define Relationships**: Use joins to establish relationships between cubes.

4. **Set Primary Keys**: Define primary keys for all cubes to ensure proper join behavior.

5. **Pre-aggregate Common Queries**: Use pre-aggregations for commonly queried data patterns.

6. **Use Segments**: Create segments for common filtering patterns.

7. **Organize by Domain**: Split schemas by business domain for better maintainability. 