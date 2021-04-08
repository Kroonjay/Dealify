DELIMITER //
CREATE PROCEDURE SetDeletedCraigslistItem (
   IN item_id_param INT,
   IN is_deleted_param INT
)
BEGIN
UPDATE CraigslistItems SET is_deleted = is_deleted_param, last_seen_at = CURRENT_TIMESTAMP WHERE item_id = item_id_param LIMIT 1;
SELECT * FROM CraigslistItems WHERE item_id = item_id_param;
END //