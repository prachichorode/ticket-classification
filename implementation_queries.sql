-- ============================================================
-- AI-BASED CUSTOMER SUPPORT & TICKET MANAGEMENT SYSTEM
-- DBMS IMPLEMENTATION QUERIES
-- Database: ticket_system_v2
-- ============================================================


USE ticket_system_v2;


-- ============================================================
-- 1. SHOW DATABASE TABLES
-- ============================================================

SHOW TABLES;


-- ============================================================
-- 2. INSERT - CATEGORY
-- ============================================================

-- Check existing categories first

SELECT *
FROM categories;


-- Insert a new category

INSERT INTO categories (category_name)
VALUES ('Network Issue');


-- Verify

SELECT *
FROM categories;


-- ============================================================
-- 3. INSERT - USER
-- ============================================================

-- Normally users are created through the Flask Registration page.
-- For database demonstration, existing users can be viewed using:

SELECT
    user_id,
    full_name,
    username,
    email,
    role,
    created_at
FROM users;


-- ============================================================
-- 4. INSERT - TICKET
-- ============================================================

-- First check users

SELECT
    user_id,
    full_name,
    username,
    role
FROM users;


-- Check categories

SELECT
    category_id,
    category_name
FROM categories;


-- Example ticket insertion
-- Replace user_id and category_id with IDs that actually exist.

INSERT INTO tickets
(
    user_id,
    category_id,
    subject,
    description,
    priority,
    status
)
VALUES
(
    1,
    1,
    'Unable to login',
    'Customer is unable to login to the support system.',
    'High',
    'Open'
);


-- Verify inserted ticket

SELECT *
FROM tickets
ORDER BY ticket_id DESC;


-- ============================================================
-- 5. SELECT - ALL USERS
-- ============================================================

SELECT *
FROM users;


-- ============================================================
-- 6. SELECT - ALL CATEGORIES
-- ============================================================

SELECT *
FROM categories;


-- ============================================================
-- 7. SELECT - ALL TICKETS
-- ============================================================

SELECT *
FROM tickets;


-- ============================================================
-- 8. SELECT - OPEN TICKETS
-- ============================================================

SELECT
    ticket_id,
    subject,
    priority,
    status,
    created_at
FROM tickets
WHERE status = 'Open';


-- ============================================================
-- 9. SELECT - CRITICAL TICKETS
-- ============================================================

SELECT
    ticket_id,
    subject,
    description,
    priority,
    status
FROM tickets
WHERE priority = 'Critical';


-- ============================================================
-- 10. SELECT - HIGH PRIORITY TICKETS
-- ============================================================

SELECT
    ticket_id,
    subject,
    priority,
    status
FROM tickets
WHERE priority = 'High';


-- ============================================================
-- 11. UPDATE - TICKET STATUS
-- ============================================================

-- Example:
-- Change ticket #1 to In Progress

UPDATE tickets
SET status = 'In Progress'
WHERE ticket_id = 1;


-- Verify

SELECT
    ticket_id,
    subject,
    status
FROM tickets
WHERE ticket_id = 1;


-- ============================================================
-- 12. UPDATE - TICKET PRIORITY
-- ============================================================

UPDATE tickets
SET priority = 'Critical'
WHERE ticket_id = 1;


-- Verify

SELECT
    ticket_id,
    subject,
    priority
FROM tickets
WHERE ticket_id = 1;


-- ============================================================
-- 13. UPDATE - STATUS + PRIORITY
-- ============================================================

UPDATE tickets
SET
    status = 'Resolved',
    priority = 'High'
WHERE ticket_id = 1;


-- Verify

SELECT
    ticket_id,
    subject,
    priority,
    status
FROM tickets
WHERE ticket_id = 1;


-- ============================================================
-- 14. DELETE - TEST TICKET
-- ============================================================

-- FIRST check the ticket

SELECT *
FROM tickets
WHERE ticket_id = 1;


-- Delete only when you actually want to delete it.

-- DELETE FROM tickets
-- WHERE ticket_id = 1;


-- ============================================================
-- 15. JOIN - TICKETS + USERS
-- ============================================================

SELECT
    t.ticket_id,
    u.full_name,
    u.username,
    u.email,
    t.subject,
    t.priority,
    t.status
FROM tickets t
JOIN users u
    ON t.user_id = u.user_id;


-- ============================================================
-- 16. JOIN - TICKETS + USERS + CATEGORIES
-- ============================================================

SELECT
    t.ticket_id,
    u.full_name,
    u.email,
    c.category_name,
    t.subject,
    t.description,
    t.priority,
    t.status,
    t.created_at
FROM tickets t
JOIN users u
    ON t.user_id = u.user_id
LEFT JOIN categories c
    ON t.category_id = c.category_id
ORDER BY t.created_at DESC;


-- ============================================================
-- 17. JOIN - CUSTOMER TICKETS
-- ============================================================

SELECT
    u.full_name,
    u.email,
    t.ticket_id,
    t.subject,
    t.priority,
    t.status
FROM users u
JOIN tickets t
    ON u.user_id = t.user_id
WHERE u.role = 'Customer';


-- ============================================================
-- 18. GROUP BY - TICKETS BY PRIORITY
-- ============================================================

SELECT
    priority,
    COUNT(*) AS total_tickets
FROM tickets
GROUP BY priority;


-- ============================================================
-- 19. GROUP BY - TICKETS BY STATUS
-- ============================================================

SELECT
    status,
    COUNT(*) AS total_tickets
FROM tickets
GROUP BY status;


-- ============================================================
-- 20. GROUP BY - TICKETS BY CATEGORY
-- ============================================================

SELECT
    c.category_name,
    COUNT(t.ticket_id) AS total_tickets
FROM categories c
LEFT JOIN tickets t
    ON c.category_id = t.category_id
GROUP BY
    c.category_id,
    c.category_name
ORDER BY total_tickets DESC;


-- ============================================================
-- 21. GROUP BY - USER WISE TICKETS
-- ============================================================

SELECT
    u.user_id,
    u.full_name,
    COUNT(t.ticket_id) AS total_tickets
FROM users u
LEFT JOIN tickets t
    ON u.user_id = t.user_id
GROUP BY
    u.user_id,
    u.full_name
ORDER BY total_tickets DESC;


-- ============================================================
-- 22. AGGREGATE - TOTAL TICKETS
-- ============================================================

SELECT
    COUNT(*) AS total_tickets
FROM tickets;


-- ============================================================
-- 23. AGGREGATE - OPEN TICKETS
-- ============================================================

SELECT
    COUNT(*) AS open_tickets
FROM tickets
WHERE status = 'Open';


-- ============================================================
-- 24. AGGREGATE - CRITICAL TICKETS
-- ============================================================

SELECT
    COUNT(*) AS critical_tickets
FROM tickets
WHERE priority = 'Critical';


-- ============================================================
-- 25. STORED PROCEDURE
-- ============================================================

CALL GetTicketStatistics();


-- ============================================================
-- 26. VIEW TICKET HISTORY
-- ============================================================

SELECT
    history_id,
    ticket_id,
    changed_by,
    old_status,
    new_status,
    remarks,
    changed_at
FROM ticket_history
ORDER BY changed_at DESC;


-- ============================================================
-- 27. TICKET HISTORY WITH USER INFORMATION
-- ============================================================

SELECT
    h.history_id,
    h.ticket_id,
    u.full_name AS changed_by_user,
    h.old_status,
    h.new_status,
    h.remarks,
    h.changed_at
FROM ticket_history h
LEFT JOIN users u
    ON h.changed_by = u.user_id
ORDER BY h.changed_at DESC;


-- ============================================================
-- 28. CHECK TRIGGERS
-- ============================================================

SHOW TRIGGERS;


-- ============================================================
-- 29. CHECK STORED PROCEDURE
-- ============================================================

SHOW PROCEDURE STATUS
WHERE Db = 'ticket_system_v2';


-- ============================================================
-- 30. DAILY TICKET ANALYTICS
-- ============================================================

SELECT
    DATE(created_at) AS ticket_date,
    COUNT(*) AS total_tickets
FROM tickets
GROUP BY DATE(created_at)
ORDER BY ticket_date;


-- ============================================================
-- 31. CATEGORY + PRIORITY ANALYSIS
-- ============================================================

SELECT
    c.category_name,
    t.priority,
    COUNT(*) AS total_tickets
FROM tickets t
LEFT JOIN categories c
    ON t.category_id = c.category_id
GROUP BY
    c.category_name,
    t.priority
ORDER BY
    c.category_name,
    total_tickets DESC;


-- ============================================================
-- 32. STATUS + PRIORITY ANALYSIS
-- ============================================================

SELECT
    status,
    priority,
    COUNT(*) AS total_tickets
FROM tickets
GROUP BY
    status,
    priority
ORDER BY
    status,
    priority;


-- ============================================================
-- 33. CUSTOMER TICKET SUMMARY
-- ============================================================

SELECT
    u.full_name,
    COUNT(t.ticket_id) AS total_tickets,
    SUM(t.status = 'Open') AS open_tickets,
    SUM(t.status = 'In Progress') AS in_progress,
    SUM(t.status = 'Resolved') AS resolved
FROM users u
LEFT JOIN tickets t
    ON u.user_id = t.user_id
WHERE u.role = 'Customer'
GROUP BY
    u.user_id,
    u.full_name;


-- ============================================================
-- 34. FIND UNRESOLVED HIGH/CRITICAL TICKETS
-- ============================================================

SELECT
    t.ticket_id,
    u.full_name,
    c.category_name,
    t.subject,
    t.priority,
    t.status
FROM tickets t
JOIN users u
    ON t.user_id = u.user_id
LEFT JOIN categories c
    ON t.category_id = c.category_id
WHERE
    t.priority IN ('High', 'Critical')
    AND t.status NOT IN ('Resolved', 'Closed')
ORDER BY
    t.priority DESC;


-- ============================================================
-- 35. TICKETS CREATED RECENTLY
-- ============================================================

SELECT
    ticket_id,
    subject,
    priority,
    status,
    created_at
FROM tickets
ORDER BY created_at DESC
LIMIT 10;


-- ============================================================
-- 36. SQL QUERY HISTORY
-- ============================================================

SELECT
    h.command_id,
    u.username,
    h.sql_command,
    h.execution_status,
    h.executed_at
FROM sql_command_history h
JOIN users u
    ON h.user_id = u.user_id
ORDER BY h.executed_at DESC;


-- ============================================================
-- 37. SUCCESSFUL SQL COMMANDS
-- ============================================================

SELECT
    command_id,
    user_id,
    sql_command,
    executed_at
FROM sql_command_history
WHERE execution_status = 'SUCCESS'
ORDER BY executed_at DESC;


-- ============================================================
-- 38. FAILED SQL COMMANDS
-- ============================================================

SELECT
    command_id,
    user_id,
    sql_command,
    executed_at
FROM sql_command_history
WHERE execution_status = 'FAILED'
ORDER BY executed_at DESC;


-- ============================================================
-- 39. DATABASE STRUCTURE
-- ============================================================

DESCRIBE users;

DESCRIBE categories;

DESCRIBE tickets;

DESCRIBE ticket_history;

DESCRIBE sql_command_history;


-- ============================================================
-- 40. FINAL DATABASE CHECK
-- ============================================================

SELECT
    'Users' AS table_name,
    COUNT(*) AS total_records
FROM users

UNION ALL

SELECT
    'Categories',
    COUNT(*)
FROM categories

UNION ALL

SELECT
    'Tickets',
    COUNT(*)
FROM tickets

UNION ALL

SELECT
    'Ticket History',
    COUNT(*)
FROM ticket_history

UNION ALL

SELECT
    'SQL Command History',
    COUNT(*)
FROM sql_command_history;