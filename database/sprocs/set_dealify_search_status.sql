DELIMITER //
CREATE PROCEDURE SetDormantDealifySearch (
    IN search_id_param INT
)
BEGIN
UPDATE DealifySearches SET search_status = 0 WHERE search_id = search_id_param;
END //