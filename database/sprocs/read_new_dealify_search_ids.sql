DELIMITER //
CREATE PROCEDURE ReadNewDealifySearchIds ()
BEGIN
SELECT search_id FROM DealifySearches WHERE search_status = 4;
END //