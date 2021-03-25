DELIMITER //
CREATE PROCEDURE ReadCraigslistItemsBySearchId (
    IN search_id_param INT
) BEGIN
SELECT item_id, item_name, price, source_url, tags, created_at, last_seen_at FROM CraigslistItems WHERE search_id = search_id_param;
END //