DELIMITER //
CREATE PROCEDURE CreateConfigKey(
    IN key_name_param NVARCHAR(90),
    IN config_value_param JSON,
    IN notes_param TEXT
)
BEGIN
INSERT INTO
  ConfigKeys (
    key_name,
    config_value,
    notes
  )
VALUES
  (
    key_name_param,
    config_value_param,
    notes_param
  ) ON DUPLICATE KEY
UPDATE
  config_value = config_value_param,
  last_updated_at = CURRENT_TIMESTAMP();
END //