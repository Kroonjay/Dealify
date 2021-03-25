DELIMITER //
CREATE PROCEDURE StartOverdueCraigslistQuery (
    IN query_id_param INT
)
BEGIN
UPDATE CraigslistQueries SET query_status = 1, last_execution_at = CURRENT_TIMESTAMP WHERE query_id = query_id_param AND query_status = 2;
SELECT query_id, search_id, query, site_id, area, category, search_titles, require_image, posted_today FROM CraigslistQueries WHERE query_id = query_id_param AND query_status = 1;
END //