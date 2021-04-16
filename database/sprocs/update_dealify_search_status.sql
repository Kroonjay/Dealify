DELIMITER //

CREATE PROCEDURE UpdateDealifySearchStatus(
    IN search_id_param INT,
    IN new_status_param INT
)
BEGIN
UPDATE DealifySearches SET search_status = new_status_param WHERE search_id = search_id_param LIMIT 1;
SELECT * FROM DealifySearches WHERE search_id = search_id_param LIMIT 1;
END //