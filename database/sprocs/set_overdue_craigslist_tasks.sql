DELIMITER //
CREATE PROCEDURE SetOverdueCraigslistQueries()
BEGIN
UPDATE CraigslistQueries SET query_status = 2 WHERE ADDDATE(last_execution_at, INTERVAL @interval_mins MINUTE) < CURRENT_TIMESTAMP AND query_status = 0;
SELECT COUNT(query_id) FROM CraigslistQueries WHERE query_status = 2;
END //