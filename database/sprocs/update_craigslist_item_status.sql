DELIMITER //
CREATE PROCEDURE UpdateCraigslistItemStatus(
    IN item_id_param INT,
    IN new_status_param INT
)
BEGIN
UPDATE CraigslistItems SET item_status = new_status_param WHERE item_id = item_id_param LIMIT 1;
SELECT * FROM CraigslistItems WHERE item_id = item_id_param;
END //