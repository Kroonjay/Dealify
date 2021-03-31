DELIMITER //
CREATE PROCEDURE UserDisableDealifySearch (
    IN search_id_param INT
) BEGIN
SELECT search_id INTO @search_id FROM DealifySearches WHERE search_id = search_id_param FOR UPDATE;
UPDATE CraigslistQueries SET query_status = 3 WHERE search_id = @search_id;
UPDATE DealifySearches SET search_status = 3 WHERE search_id = @search_id;
SELECT search_id, search_status FROM DealifySearches WHERE search_id = @search_id;
END //