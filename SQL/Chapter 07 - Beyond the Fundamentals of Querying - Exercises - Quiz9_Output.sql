/**************************************************************************
 * (C) Copyright 2012-2014 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/

--solution
USE CS120_2013Fall_rstone215;

IF OBJECT_ID('dbo.Orders', 'U') IS NOT NULL DROP TABLE dbo.Orders;

CREATE TABLE dbo.Orders
(
orderid INT NOT NULL,
orderdate DATE NOT NULL,
empid INT NOT NULL,
custid VARCHAR(5) NOT NULL,
qty INT NOT NULL,
CONSTRAINT PK_Orders PRIMARY KEY(orderid)
);

INSERT INTO dbo.Orders(orderid, orderdate, empid, custid, qty)
VALUES
(30001, '20070802', 3, 'A', 10),
(10001, '20071224', 2, 'A', 12),
(10005, '20071224', 1, 'B', 20),
(40001, '20080109', 2, 'A', 40),
(10006, '20080118', 1, 'C', 14),
(20001, '20080212', 2, 'B', 12),
(40005, '20090212', 3, 'A', 10),
(20002, '20090216', 1, 'C', 20),
(30003, '20090418', 2, 'B', 15),
(30004, '20070418', 3, 'C', 22),
(30007, '20090907', 3, 'D', 30);

SELECT * FROM dbo.Orders;

-- 1
-- Write a query against the dbo.Orders table that computes for each
-- customer order, a rank, a dense rank and NTILE(2) 
-- partitioned by custid, ordered by qty 

-- Desired output:
custid orderid     qty         rnk                  drnk                 NTILE
------ ----------- ----------- -------------------- -------------------- --------------------
A      30001       10          1                    1                    1
A      40005       10          1                    1                    1
A      10001       12          3                    2                    2
A      40001       40          4                    3                    2
B      20001       12          1                    1                    1
B      30003       15          2                    2                    1
B      10005       20          3                    3                    2
C      10006       14          1                    1                    1
C      20002       20          2                    2                    1
C      30004       22          3                    3                    2
D      30007       30          1                    1                    1

(11 row(s) affected)

-- Solutions
SELECT custid, orderid, qty,
  RANK() OVER(PARTITION BY custid ORDER BY qty) AS rnk,
  DENSE_RANK() OVER(PARTITION BY custid ORDER BY qty) AS drnk,
  NTILE(2) OVER(PARTITION BY custid ORDER BY qty) AS NTILE
FROM dbo.Orders;


-- 2
-- Write a query against the dbo.Orders table that computes for each
-- customer order:
-- * the difference between the current order quantity
--   and the customer's previous order quantity
-- * the difference between the current order quantity
-- * the SUM(qty) PARTITION by custid
--   and the customer's next order quantity.

-- Desired output:
custid orderid     qty         diffprev    diffnext    custtotalvalue
------ ----------- ----------- ----------- ----------- --------------
A      30001       10          NULL        -2          72
A      10001       12          2           -28         72
A      40001       40          28          30          72
A      40005       10          -30         NULL        72
B      10005       20          NULL        8           47
B      20001       12          -8          -3          47
B      30003       15          3           NULL        47
C      30004       22          NULL        8           56
C      10006       14          -8          -6          56
C      20002       20          6           NULL        56
D      30007       30          NULL        NULL        30

(11 row(s) affected)

-- Solutions
SELECT custid, orderid, qty,
  qty - LAG(qty)  OVER(PARTITION BY custid
                      ORDER BY orderdate, orderid) AS diffprev,
  qty - LEAD(qty) OVER(PARTITION BY custid
                       ORDER BY orderdate, orderid) AS diffnext,
         SUM(qty) OVER(PARTITION BY custid) AS custtotalvalue
FROM dbo.Orders;
