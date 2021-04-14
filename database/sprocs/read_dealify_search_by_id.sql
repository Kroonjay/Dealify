DELIMITER //
CREATE PROCEDURE ReadDealifySearchById (
    IN search_id_param INT
) BEGIN
SELECT * FROM DealifySearches WHERE search_id = search_id_param LIMIT 1;
END //