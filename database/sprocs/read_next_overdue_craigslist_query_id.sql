DELIMITER //
CREATE PROCEDURE ReadNextOverdueCraigslistQueryId ()
BEGIN
SELECT query_id FROM CraigslistQueries WHERE query_status = 2 ORDER BY last_execution_at ASC LIMIT 1;
END //