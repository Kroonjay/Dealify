DELIMITER //

CREATE PROCEDURE ReadDealifySearchesByStatus(
    IN search_status_param INT,
    IN limit_param INT
)
BEGIN
SELECT * FROM DealifySearches WHERE search_status = search_status_param LIMIT limit_param;
END //