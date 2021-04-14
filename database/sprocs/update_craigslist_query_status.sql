DELIMITER //
CREATE PROCEDURE UpdateCraigslistQueryStatus(
    IN query_id_param INT,
    IN new_status_param INT
)
BEGIN
UPDATE CraigslistQueries SET query_status = new_status_param WHERE query_id = query_id_param LIMIT 1;
SELECT * FROM CraigslistQueries WHERE query_id = query_id_param LIMIT 1;
END //