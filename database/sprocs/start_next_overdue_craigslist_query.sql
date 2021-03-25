DELIMITER //
CREATE PROCEDURE StartNextOverdueCraigslistQuery ()
BEGIN
SELECT query_id, search_id, interval_mins INTO @query_id, @search_id, @interval_mins FROM CraigslistQueries WHERE next_execution_at < CURRENT_TIMESTAMP AND query_status = 0 ORDER BY next_execution_at ASC LIMIT 1 FOR UPDATE;
UPDATE CraigslistQueries SET query_status = 1, last_execution_at = CURRENT_TIMESTAMP, next_execution_at = ADDDATE(CURRENT_TIMESTAMP, INTERVAL @interval_mins MINUTE) WHERE query_id = @query_id;
UPDATE DealifySearches SET search_status = 1 WHERE search_id = @search_id;
SELECT query_id, search_id, query, site_id, area, category, search_titles, require_image, posted_today FROM CraigslistQueries WHERE query_id = @query_id;
END //