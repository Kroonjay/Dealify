DELIMITER //
CREATE PROCEDURE ReadConfigKeyByName (
    IN key_name_param NVARCHAR(90)
) BEGIN
UPDATE ConfigKeys SET last_used_at = CURRENT_TIMESTAMP WHERE key_name = key_name_param LIMIT 1;
SELECT * FROM ConfigKeys WHERE key_name = key_name_param LIMIT 1;
END //