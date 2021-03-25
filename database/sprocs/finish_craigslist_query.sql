DELIMITER //
CREATE PROCEDURE FinishCraigslistQuery (
    IN query_id_param INT
)
BEGIN
SELECT query_id, search_id INTO @query_id, @search_id FROM CraigslistQueries WHERE query_id = query_id_param LIMIT 1 FOR UPDATE;
UPDATE CraigslistQueries SET query_status = 0 WHERE query_id = @query_id;
UPDATE DealifySearches SET search_status = 0 WHERE search_id = @search_id;
SELECT query_id, query_status from CraigslistQueries WHERE query_id = query_id_param;
END //