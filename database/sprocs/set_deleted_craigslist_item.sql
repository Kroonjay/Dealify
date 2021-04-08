DELIMITER //
CREATE PROCEDURE SetDeletedCraigslistItem (
   IN item_id_param INT
)
BEGIN
UPDATE CraigslistItems SET is_deleted = 1, last_seen_at = CURRENT_TIMESTAMP WHERE item_id = item_id_param LIMIT 1;
SELECT * FROM CraigslistItems WHERE item_id = item_id_param;
END //