| TOP 20 SQL QUERIES

1.  **Retrieve all records from a table:**
    
    ```sql
    SELECT * FROM table_name;
    ```
    
2.  **Retrieve specific columns from a table:**
    
    ```sql
    SELECT column1, column2 FROM table_name;
    ```
    
3.  **Retrieve records with a specific condition:**
    
    ```sql
    SELECT * FROM table_name WHERE condition;
    ```
    
4.  **Retrieve distinct values from a column:**
    
    ```sql
    SELECT DISTINCT column_name FROM table_name;
    ```
    
5.  **Count the number of records in a table:**
    
    ```sql
    SELECT COUNT(*) FROM table_name;
    ```
    
6.  **Retrieve records sorted in ascending order:**
    
    ```sql
    SELECT * FROM table_name ORDER BY column_name ASC;
    ```
    
7.  **Retrieve records sorted in descending order:**
    
    ```sql
    SELECT * FROM table_name ORDER BY column_name DESC;
    ```
    
8.  **Retrieve records using pattern matching (LIKE):**
    
    ```sql
    SELECT * FROM table_name WHERE column_name LIKE 'pattern';
    ```
    
9.  **Retrieve records using wildcard characters (%):**
    
    ```sql
    SELECT * FROM table_name WHERE column_name LIKE 'pattern%';
    ```
    
10.  **Retrieve records with NULL values:**
    
    ```sql
    SELECT * FROM table_name WHERE column_name IS NULL;
    ```
    
11.  **Retrieve records between two dates:**
    
    ```sql
    SELECT * FROM table_name WHERE date_column BETWEEN 'start_date' AND 'end_date';
    ```
    
12.  **Retrieve records from multiple tables (JOIN):**
    
    ```sql
    SELECT t1.column1, t2.column2
    FROM table1 t1
    INNER JOIN table2 t2 ON t1.key = t2.key;
    ```
    
13.  **Retrieve aggregated data (GROUP BY):**
    
    ```sql
    SELECT column, COUNT(*)
    FROM table_name
    GROUP BY column;
    ```
    
14.  **Retrieve aggregated data with conditions (HAVING):**
    
    ```sql
    SELECT column, COUNT(*)
    FROM table_name
    GROUP BY column
    HAVING COUNT(*) > threshold;
    ```
    
15.  **Insert a new record into a table:**
    
    ```sql
    INSERT INTO table_name (column1, column2) VALUES (value1, value2);
    ```
    
16.  **Update records in a table:**
    
    ```sql
    UPDATE table_name SET column1 = new_value WHERE condition;
    ```
    
17.  **Delete records from a table:**
    
    ```sql
    DELETE FROM table_name WHERE condition;
    ```
    
18.  **Retrieve top N records from a table:**
    
    ```sql
    SELECT TOP N * FROM table_name;
    ```
    
19.  **Retrieve records with pagination:**
    
    ```sql
    SELECT * FROM table_name LIMIT offset, limit;
    ```
    
20.  **Retrieve records using subqueries:**
    
    ```sql
    SELECT * FROM table_name WHERE column IN (SELECT column FROM another_table WHERE condition);
    ```
    