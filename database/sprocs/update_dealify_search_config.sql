DELIMITER //
CREATE PROCEDURE UpdateDealifySearchConfig(
    IN search_id_param INT,
    IN new_config_param JSON
)
BEGIN
UPDATE DealifySearches SET search_config = new_config_param WHERE search_id = search_id_param LIMIT 1;
SELECT * FROM DealifySearches WHERE search_id = search_id_param LIMIT 1;
END //