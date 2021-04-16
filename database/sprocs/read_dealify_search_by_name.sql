DELIMITER //

CREATE PROCEDURE ReadDealifySearchByName(
    IN search_name_param NVARCHAR(90)
)
BEGIN
SELECT * FROM DealifySearches WHERE search_name = search_name_param LIMIT 1;
END //