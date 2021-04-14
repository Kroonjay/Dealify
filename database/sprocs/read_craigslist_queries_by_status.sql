DELIMITER //
CREATE PROCEDURE ReadCraigslistQueriesByStatus(
    IN status_param INT,
    IN limit_param INT
)
BEGIN
SELECT * FROM CraigslistQueries WHERE query_status = status_param LIMIT limit_param;
END //