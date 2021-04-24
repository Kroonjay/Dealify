DELIMITER //
CREATE PROCEDURE ReadOldestCraigslistQueries (
    IN status_param INT,
    IN limit_param INT 
)
BEGIN
SELECT * FROM CraigslistQueries WHERE query_status = status_param ORDER BY last_execution_at ASC LIMIT limit_param;
END //