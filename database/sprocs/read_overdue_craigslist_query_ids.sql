DELIMITER //
CREATE PROCEDURE ReadOverdueCraigslistQueryIds (
    IN limit_param INT
)
BEGIN
SELECT query_id from CraigslistQueries WHERE query_sta

