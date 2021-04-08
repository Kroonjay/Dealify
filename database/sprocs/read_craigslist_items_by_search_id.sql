DELIMITER //
CREATE PROCEDURE ReadCraigslistItemsBySearchId (
    IN search_id_param INT,
    IN limit_param INT
) BEGIN
SELECT * FROM CraigslistItems WHERE search_id = search_id_param LIMIT limit_param;
END //