DELIMITER //
CREATE PROCEDURE ReadDealifySearchById (
    IN search_id_param INT
) BEGIN
SELECT search_id,search_status,search_name,sources,search_config,created_at FROM DealifySearches WHERE search_id = search_id_param LIMIT 1;
END //